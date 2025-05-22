import logging
from typing import List, Optional, Any

from presidio_analyzer import AnalyzerEngineProvider, AnalyzerRequest
from app.config import get_settings
from app.models.analysis import AnalyzeRequest, EntityResult

from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer.predefined_recognizers import TransformersRecognizer

logger = logging.getLogger(__name__)

class AnalyzerService:
    def __init__(self, settings=None):
        settings = settings or get_settings()
        
        provider = AnalyzerEngineProvider(
            # analyzer_engine_conf_file=settings.analyzer_conf_file,
            # nlp_engine_conf_file=settings.nlp_conf_file,
        )
        
        self.engine = provider.create_engine()
        

    def analyze(self, req_model: AnalyzeRequest) -> List[EntityResult]:
        if not req_model.text or not req_model.language:
            return []
            
        try:
            req = AnalyzerRequest(req_model.model_dump(exclude_none=True))
            results = self.engine.analyze(
                text=req.text,
                language=req.language,
                correlation_id=req.correlation_id,
                score_threshold=req.score_threshold,
                entities=req.entities,
                return_decision_process=req.return_decision_process,
                ad_hoc_recognizers=req.ad_hoc_recognizers,
                context=req.context,
                allow_list=req.allow_list,
                allow_list_match=req.allow_list_match,
                regex_flags=req.regex_flags,
            )
            return [EntityResult(**r.to_dict()) for r in results]
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise RuntimeError(f"Failed to analyze text: {str(e)}") from e
            
    def get_recognizers(self, language: Optional[str] = None) -> List[Any]:
        return self.engine.get_recognizers(language=language)
            
    def get_supported_entities(self, language: Optional[str] = None) -> List[str]:
        return self.engine.get_supported_entities(language=language)
