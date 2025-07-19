"""Vector store service using Milvus Lite."""
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
import logging
from pathlib import Path

from pymilvus import MilvusClient, DataType, CollectionSchema, FieldSchema
from pymilvus.milvus_client import IndexParams
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


@dataclass
class VectorSearchResult:
    """Result from vector similarity search."""
    id: str
    score: float
    metadata: Dict[str, Any]
    text: Optional[str] = None


class VectorStoreService:
    """Service for managing resume embeddings with Milvus Lite."""
    
    def __init__(self, config: Dict[str, Any], openai_client: AsyncOpenAI):
        """Initialize vector store service."""
        self.config = config
        self.openai_client = openai_client
        self.collection_name = config["milvus_collection_name"]
        self.dimension = config["embedding_dimension"]
        self.milvus_file = Path(config["milvus_lite_file"])
        self.client: Optional[MilvusClient] = None
        self.collection = None
    
    async def initialize(self) -> None:
        """Initialize Milvus Lite connection and create collection."""
        # Ensure directory exists
        self.milvus_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize Milvus client
        self.client = MilvusClient(str(self.milvus_file))
        
        # Create collection if it doesn't exist
        if not self.client.has_collection(self.collection_name):
            schema = self._create_collection_schema()
            self.client.create_collection(
                collection_name=self.collection_name,
                schema=schema,
                consistency_level="Strong"
            )
            logger.info(f"Created collection: {self.collection_name}")
            
            # Create index for vector field
            self._create_index()
        
        self.collection = self.collection_name
        logger.info("Vector store initialized successfully")
    
    def _create_collection_schema(self) -> CollectionSchema:
        """Create Milvus collection schema."""
        fields = [
            FieldSchema(
                name="id",
                dtype=DataType.VARCHAR,
                is_primary=True,
                max_length=256
            ),
            FieldSchema(
                name="embedding",
                dtype=DataType.FLOAT_VECTOR,
                dim=self.dimension
            ),
            FieldSchema(
                name="text",
                dtype=DataType.VARCHAR,
                max_length=65535
            ),
            FieldSchema(
                name="metadata",
                dtype=DataType.JSON
            )
        ]
        
        return CollectionSchema(
            fields=fields,
            description="Resume embeddings collection"
        )
    
    def _create_index(self) -> None:
        """Create index for vector field."""
        index_params = IndexParams()
        index_params.add_index(
            field_name="embedding",
            metric_type="COSINE",
            index_type="IVF_FLAT",
            params={"nlist": 128}
        )
        
        self.client.create_index(
            collection_name=self.collection_name,
            index_params=index_params
        )
        logger.info("Created index for embedding field")
    
    async def create_embedding(self, text: str) -> List[float]:
        """Create embedding for text using OpenAI."""
        response = await self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    async def store_resume(
        self,
        resume_id: str,
        text: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Store resume with embedding."""
        # Create embedding
        embedding = await self.create_embedding(text)
        
        # Store in Milvus
        return await self._store_embedding(resume_id, embedding, metadata, text)
    
    async def _store_embedding(
        self,
        doc_id: str,
        embedding: List[float],
        metadata: Dict[str, Any],
        text: Optional[str] = None
    ) -> str:
        """Store embedding in Milvus."""
        if len(embedding) != self.dimension:
            raise ValueError(
                f"Embedding dimension {len(embedding)} doesn't match "
                f"expected dimension {self.dimension}"
            )
        
        data = {
            "id": doc_id,
            "embedding": embedding,
            "metadata": metadata,
            "text": text or ""
        }
        
        self.client.insert(
            collection_name=self.collection_name,
            data=[data]
        )
        
        return doc_id
    
    async def search_similar_resumes(
        self,
        query: str,
        limit: int = 10,
        filter_expr: Optional[str] = None
    ) -> List[VectorSearchResult]:
        """Search for similar resumes based on query."""
        # Create query embedding
        query_embedding = await self.create_embedding(query)
        
        # Search in Milvus
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10}
        }
        
        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_embedding],
            limit=limit,
            filter=filter_expr,
            output_fields=["id", "metadata", "text"],
            search_params=search_params
        )
        
        # Convert to VectorSearchResult
        search_results = []
        if results and len(results[0]) > 0:
            for hit in results[0]:
                search_results.append(
                    VectorSearchResult(
                        id=hit["entity"]["id"],
                        score=hit["distance"],
                        metadata=hit["entity"]["metadata"],
                        text=hit["entity"].get("text")
                    )
                )
        
        return search_results
    
    async def get_resume_by_id(self, resume_id: str) -> Optional[VectorSearchResult]:
        """Get resume by ID."""
        try:
            results = self.client.get(
                collection_name=self.collection_name,
                ids=[resume_id],
                output_fields=["id", "metadata", "text"]
            )
            
            if results and len(results) > 0:
                entity = results[0]
                return VectorSearchResult(
                    id=entity["id"],
                    score=1.0,
                    metadata=entity["metadata"],
                    text=entity.get("text")
                )
        except Exception as e:
            logger.error(f"Error getting resume {resume_id}: {e}")
        
        return None
    
    async def update_resume(
        self,
        resume_id: str,
        text: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Update existing resume."""
        try:
            # Delete old version
            self.client.delete(
                collection_name=self.collection_name,
                ids=[resume_id]
            )
            
            # Store new version
            await self.store_resume(resume_id, text, metadata)
            return True
        except Exception as e:
            logger.error(f"Error updating resume {resume_id}: {e}")
            return False
    
    async def delete_resume(self, resume_id: str) -> bool:
        """Delete resume from store."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                ids=[resume_id]
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting resume {resume_id}: {e}")
            return False
    
    async def batch_store_resumes(
        self,
        resumes: List[Dict[str, Any]]
    ) -> List[str]:
        """Store multiple resumes efficiently."""
        # Create embeddings in parallel
        texts = [r["text"] for r in resumes]
        embeddings = await asyncio.gather(
            *[self.create_embedding(text) for text in texts]
        )
        
        # Prepare batch data
        batch_data = []
        for i, resume in enumerate(resumes):
            batch_data.append({
                "id": resume["id"],
                "embedding": embeddings[i],
                "metadata": resume["metadata"],
                "text": resume["text"]
            })
        
        # Insert batch
        self.client.insert(
            collection_name=self.collection_name,
            data=batch_data
        )
        
        return [r["id"] for r in resumes]
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        stats = self.client.get_collection_stats(self.collection_name)
        return {
            "collection_name": self.collection_name,
            "total_entities": stats.get("row_count", 0),
            "index_status": "ready"
        }
    
    async def close(self) -> None:
        """Close Milvus connection."""
        if self.client:
            # Milvus Lite doesn't require explicit close
            self.client = None
            logger.info("Vector store closed")