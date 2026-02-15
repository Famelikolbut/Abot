import asyncio
import json
import logging
from datetime import datetime
from database.database import AsyncSessionLocal
from database.models import Video, VideoSnapshot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def load_data(file_path: str):
    logger.info(f"Loading data from {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    async with AsyncSessionLocal() as session:
        try:
            videos_data = data.get('videos', [])
            logger.info(f"Found {len(videos_data)} videos.")

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
                    logger.info(f"Processed {i} videos...")
            
            await session.commit()
            logger.info("Data loading complete.")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            await session.rollback()
            raise

async def main():
    # Only load data, schema is handled by migrations
    await load_data('videos.json')

if __name__ == "__main__":
    asyncio.run(main())
