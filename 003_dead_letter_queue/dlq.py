import json
import logging
from typing import Dict,Any,Iterable,List,Tuple
from datetime import datetime,UTC
from dataclasses import dataclass,field
from pathlib import Path
from enum import Enum
from collections import Counter



#configure logging
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)



#pipeline stage constants
class Stage(str,Enum):
    VALIDATE = "Validate"
    TRANSFORM = "Transform"
    LOAD = "Load"

#custom exceptions for pipeline
class PipelineError(Exception):
    pass

class ValidationError(PipelineError):
    pass

class TransfromError(PipelineError):
    pass


#dataclass auto generates class methords , including constructors and all 
@dataclass
#this class holds all the information about the failed record
class Deadletter:
    timestamp : datetime
    recordId : str
    lineNumber: int
    stage : Stage
    rawRecord: str
    errortype : str
    errorMsg : str
    context : Dict[str,Any]
    retrycount : int = 0


@dataclass
class PipleineStats:
#this class holds info about pipleline's processing metrices
     totalProcessed : int = 0    
     successful : int = 0 
     failed: int = 0 
     errortypes: Counter = field(default_factory=Counter) 

     def recordSuccess(self):
         self.totalProcessed +=1
         self.successful +=1

     def recordFailure(self,errorType: str):
         self.totalProcessed +=1
         self.failed +=1
         self.errortypes[errorType] +=1

     def summary(self)-> str:
         successrate = (self.successful/self.totalProcessed * 100) if self.totalProcessed > 0 else 0

         return f"""
Pipeline Statistics : 
Total Processed : {self.totalProcessed}
Successful : {self.successful} ({successrate:.1f}%)
Failed : {self.failed}
Error Breakdowm : {dict(self.errortypes)}
""".strip()
         
#this class must never crash the main pipeline
class DeadLetterQueue:
    #initialize dlq
    def __init__(self, filepath:str, alertThreshold: int = 9):
        self.path = Path(filepath)
        self.path.parent.mkdir(parents= True , exist_ok= True)
        self.alertThreshold = alertThreshold
        self.failureCount = 0
    
    #write failed record to dlq
    def write(self,deadletter : Deadletter)-> None:

        try:
            with self.path.open("a") as file:
                json.dump(deadletter.__dict__,file,default=str)
                file.write("\n")
            self.failureCount +=1

            if self.failureCount >= self.alertThreshold : 
                self.sendAlert()

        except Exception as e:
            logger.error(f"Dlq error : failed to write dead letter : {e}")


    def sendAlert(self):
        #later we can send emails or stuff in production here
        logger.warning(f"[ALERT] QLQ threshold reached : {self.failureCount} failures")

    def readAll(self)-> list[Deadletter]:

        DeadLetters = []

        if not self.path.exists():
            return DeadLetters
        
        with self.path.open("r") as file:
            for line in file:
                try:
                    data = json.loads(line)

                    if isinstance(data['timestamp'],str):
                        data['timestamp'] = datetime.fromisoformat(data['timestamp'])

                    if isinstance(data['stage'],str):
                        data['stage'] = Stage(data['stage'])

                    DeadLetters.append(Deadletter(**data))
                
                except Exception as e:
                    logger.error(f"failed to parse deadletter : {e}")
        return DeadLetters
    
    
    def clear(self) -> None:
        #clear dlq file (after successful replay)
             
             if self.path.exists():
                 self.path.unlink()
                 logger.info("DLQ Cleared")



#validate Record
def validateRecord(record:Dict[str,Any])-> Dict[str,Any] : 

    #check if name exists
    if "name" not in record or not record["name"]:
        raise ValidationError("name is required")
    
    age = record.get("age")
    if age is None or age == "":
        record["age"] = None
    else:
        if not str(age).isdigit():
            raise ValidationError(f"age must be integer , got: {age}")
        
        #covert to int
        record["age"] = int(age)

    return record

#process Record
def processRecord(
            records: Iterable[tuple[int,Dict[str,Any]]],
            dlq:DeadLetterQueue,
            stats: PipleineStats
    ) -> None:

    for linenumber, record in records:

        recordId = record.get("id",{linenumber})

        try:
            validatedRecord = validateRecord(record)

            #transform stage

            #load stage

            #log success
            logger.info(f"f[SUCCESS] {recordId}: {validatedRecord}")
            stats.recordSuccess()
        except PipelineError as e:
            DeadLetter = Deadletter(
                timestamp= datetime.now(UTC),
                recordId=  recordId,
                lineNumber=linenumber,
                stage= Stage.VALIDATE,
                rawRecord= json.dumps(record),
                errortype= type(e).__name__,
                errorMsg=str(e),
                context={"orignal Record : " : record}
            )

            dlq.write(DeadLetter)
            logger.error(f"[failed] {recordId}  : {e}")
            stats.recordFailure(type(e).__name__)

           #continue to next record don't stop the pipeline
            continue




#replay dlq
def replayDlq(dlq: DeadLetterQueue, stats: PipleineStats)-> None:

    DeadLetters = dlq.readAll()
    logger.info(f"Replaying {len(DeadLetters)} records from DLQ")

    recordstoReplay = [
        (dl.lineNumber,json.loads(dl.rawRecord))
        for dl in DeadLetters
    ]

    #create seperate DLQ for records that still fail
    replaydlqPath = dlq.path.parent/"failedReplay.jsonl"
    replaydlqQueue = DeadLetterQueue(str(replaydlqPath))


    #reprocess all records
    processRecord(recordstoReplay,replaydlqPath,stats)

    logger.info(f"Replay Complete. Check {replaydlqQueue}for still failing records")





def main():


 records = [
(1, {"id": "rec_001", "name": "Alice", "age": "25"}),
(2, {"id": "rec_002", "name": "Bob", "age": "invalid"}),  
(3, {"id": "rec_003", "name": "Charlie", "age": ""}),
(4, {"id": "rec_004", "name": "Dave", "age": None}),
(5, {"id": "rec_005", "name": "Eve", "age": "42"}),
(6, {"id": "rec_006", "name": "", "age": "30"}),
]

        
                
 dlq = DeadLetterQueue("dead_letter/failed.jsonl", 3)
    
 stats = PipleineStats()
   
 logger.info("Starting pipeline...")
 processRecord(records, dlq, stats)
    
 logger.info("\n" + stats.summary())




if __name__ == "__main__":
    main()




