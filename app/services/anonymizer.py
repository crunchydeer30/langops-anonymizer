import logging
from typing import List, Dict, Any, Optional

from presidio_anonymizer import AnonymizerEngine, DeanonymizeEngine
from presidio_anonymizer.entities import InvalidParamError
from presidio_anonymizer.services.app_entities_convertor import AppEntitiesConvertor

from app.models.anonymization import AnonymizeRequest, AnonymizeResult, DeanonymizeRequest, DeanonymizeEntity

logger = logging.getLogger(__name__)

class AnonymizerService:    
    def __init__(self):
        logger.info("Initializing Anonymizer service")
        self.anonymizer = AnonymizerEngine()
        self.deanonymizer = DeanonymizeEngine()
    
    def anonymize(self, request: AnonymizeRequest) -> AnonymizeResult:
        try:
            analyzer_results = AppEntitiesConvertor.analyzer_results_from_json(
                request.analyzer_results
            )
            
            anonymizers_config = None
            if request.anonymizers:
                anonymizers_config = AppEntitiesConvertor.operators_config_from_json(
                    request.anonymizers
                )
                
                if AppEntitiesConvertor.check_custom_operator(anonymizers_config):
                    raise ValueError("Custom type anonymizer is not supported")
            
            result = self.anonymizer.anonymize(
                text=request.text,
                analyzer_results=analyzer_results,
                operators=anonymizers_config
            )
            
            return {
                "text": result.text,
                "items": [item.to_dict() if hasattr(item, 'to_dict') else item for item in result.items] if result.items else None
            }
        except InvalidParamError as e:
            logger.warning(f"Anonymization request failed with validation error: {str(e)}")
            raise ValueError(f"Invalid anonymization parameters: {str(e)}")
        except Exception as e:
            logger.error(f"Anonymization failed: {str(e)}")
            raise RuntimeError(f"Failed to anonymize text: {str(e)}")
    
    def deanonymize(self, request: DeanonymizeRequest) -> AnonymizeResult:
        try:
            deanonymize_entities = AppEntitiesConvertor.deanonymize_entities_from_json({
                "text": request.text,
                "entities": [entity.model_dump() for entity in request.entities]
            })
            
            deanonymize_config = None
            if request.deanonymizers:
                deanonymize_config = AppEntitiesConvertor.operators_config_from_json(
                    request.deanonymizers
                )
            
            result = self.deanonymizer.deanonymize(
                text=request.text,
                entities=deanonymize_entities,
                operators=deanonymize_config
            )
            

            return {
                "text": result.text,
                "items": [item.to_dict() if hasattr(item, 'to_dict') else item for item in result.items] if result.items else None
            }
        except InvalidParamError as e:
            logger.warning(f"Deanonymization request failed with validation error: {str(e)}")
            raise ValueError(f"Invalid deanonymization parameters: {str(e)}")
        except Exception as e:
            logger.error(f"Deanonymization failed: {str(e)}")
            raise RuntimeError(f"Failed to deanonymize text: {str(e)}")
    
    def get_anonymizers(self) -> List[str]:
        return self.anonymizer.get_anonymizers()
    
    def get_deanonymizers(self) -> List[str]:
        return self.deanonymizer.get_deanonymizers()
