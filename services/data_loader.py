import json
import logging
from datetime import datetime
from sqlalchemy import text
from database.database import engine, AsyncSessionLocal
from database.models import Video, VideoSnapshot

logger = logging.getLogger(__name__)

class DataLoader:
    async def clear_data(self):
        async with AsyncSessionLocal() as session:
            try:
                logger.info("Clearing old data...")
                await session.execute(text("TRUNCATE TABLE videos CASCADE"))
                await session.commit()
                logger.info("Data cleared.")
            except Exception as e:
                logger.error(f"Error clearing data: {e}")
                await session.rollback()
                raise

    async def load_from_file(self, file_path: str):
        logger.info(f"Loading data from {file_path}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        await self._load_json_data(data)

    async def _load_json_data(self, data: dict):
        async with AsyncSessionLocal() as session:
            try:
                videos_data = data.get('videos', [])
                logger.info(f"Found {len(videos_data)} videos to insert.")

                for i, v_data in enumerate(videos_data):
                    video = Video(
                        id=v_data['id'],
                        creator_id=v_data['creator_id'],
                        video_created_at=datetime.fromisoformat(v_data['video_created_at']),
                        views_count=v_data['views_count'],
                        likes_count=v_data['likes_count'],
                        comments_count=v_data['comments_count'],
                        reports_count=v_data['reports_count'],
                        created_at=datetime.fromisoformat(v_data['created_at']),
                        updated_at=datetime.fromisoformat(v_data['updated_at'])
                    )
                    session.add(video)

                    snapshots = []
                    for s_data in v_data.get('snapshots', []):
                        snapshot = VideoSnapshot(
                            id=s_data['id'],
                            video_id=s_data['video_id'],
                            views_count=s_data['views_count'],
                            likes_count=s_data['likes_count'],
                            comments_count=s_data['comments_count'],
                            reports_count=s_data['reports_count'],
                            delta_views_count=s_data['delta_views_count'],
                            delta_likes_count=s_data['delta_likes_count'],
                            delta_reports_count=s_data['delta_reports_count'],
                            delta_comments_count=s_data['delta_comments_count'],
                            created_at=datetime.fromisoformat(s_data['created_at']),
                            updated_at=datetime.fromisoformat(s_data['updated_at'])
                        )
                        snapshots.append(snapshot)
                    
                    session.add_all(snapshots)

                    if i % 100 == 0:
                        await session.commit()
                
                await session.commit()
                logger.info("Data loading complete.")
            except Exception as e:
                logger.error(f"Error loading data: {e}")
                await session.rollback()
                raise
