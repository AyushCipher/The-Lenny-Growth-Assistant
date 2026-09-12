import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import SessionModel, MessageModel, ArtifactModel, SystemMetricModel


@pytest.mark.asyncio
async def test_session_isolation_and_persistence(db_session: AsyncSession):
    # Create two independent sessions
    session_1 = SessionModel(
        id=str(uuid.uuid4()),
        title="Session 1: PLG Strategy",
        user_metadata={"role": "Growth PM", "team": "Activation"}
    )
    session_2 = SessionModel(
        id=str(uuid.uuid4()),
        title="Session 2: Pricing Models",
        user_metadata={"role": "Founder", "team": "Executive"}
    )
    db_session.add_all([session_1, session_2])
    await db_session.commit()

    # Add messages to Session 1
    msg1 = MessageModel(
        id=str(uuid.uuid4()),
        session_id=session_1.id,
        role="user",
        content="How should we define PQLs?"
    )
    msg2 = MessageModel(
        id=str(uuid.uuid4()),
        session_id=session_1.id,
        role="assistant",
        content="According to Elena Verna, PQLs represent product usage milestones.",
        citations=[{"guest": "Elena Verna", "source_id": "src_elena_verna_01"}]
    )
    db_session.add_all([msg1, msg2])
    await db_session.commit()

    # Add message to Session 2
    msg3 = MessageModel(
        id=str(uuid.uuid4()),
        session_id=session_2.id,
        role="user",
        content="What is Channel-Model fit?"
    )
    db_session.add(msg3)
    await db_session.commit()

    # Query Session 1 messages
    res_1 = await db_session.execute(
        select(MessageModel).where(MessageModel.session_id == session_1.id)
    )
    s1_messages = res_1.scalars().all()
    assert len(s1_messages) == 2

    # Query Session 2 messages (Context Isolation check)
    res_2 = await db_session.execute(
        select(MessageModel).where(MessageModel.session_id == session_2.id)
    )
    s2_messages = res_2.scalars().all()
    assert len(s2_messages) == 1
    assert s2_messages[0].content == "What is Channel-Model fit?"

    # Check user metadata retention
    s1_fetched = await db_session.get(SessionModel, session_1.id)
    assert s1_fetched.user_metadata["role"] == "Growth PM"
