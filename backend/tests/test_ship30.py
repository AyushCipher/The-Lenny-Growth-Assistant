import pytest
from unittest.mock import AsyncMock, patch
from app.agent.ship30_skill import ship30_skill
from app.agent.models import GenerationResult


@pytest.mark.asyncio
async def test_ship30_skill_structure_and_grounding():
    # Construct a high-signal mock Ship 30 essay conforming to ~1,250 words and Ship 30 rules
    sample_paragraphs = [
        "# The PLG Illusion: Why Most B2B Startups Mistake Self-Serve for Growth\n",
        "Most B2B founders believe that putting a self-serve checkout page on their site equals Product-Led Growth. **They are completely wrong.**\n",
        "Two years ago, you probably thought self-serve meant zero sales headcount. You watched Slack and Notion scale virally and assumed your developer tool could do the same without friction. But when conversion rates stalled at 0.8%, you realized that self-serve without activation is just an expensive top-of-funnel leak.\n",
        "### Pillar 1: The Anatomy of a Real PQL\n",
        "A signup is not a lead. In true Product-Led Growth, the product is your primary acquisition and retention engine [[Elena Verna - PLG & Growth]](src_elena_verna_01). When users hit core product milestones—like inviting 5 collaborators within 7 days—they become Product-Qualified Leads (PQLs). **Product-Led Sales is not the opposite of PLG; it is the ultimate monetization multiplier.**\n",
        "### Pillar 2: High Agency Execution in Growth Experiments\n",
        "Growth requires bending reality to your will. When experiments fail, low-agency teams blame market conditions [[Shreyas Doshi - Product Strategy]](src_shreyas_doshi_01). High-agency product leaders diagnose the exact drop-off in the user journey and iterate within 48 hours. **High agency is the single biggest determinant of product success.**\n",
        "### Pillar 3: Growth Loops Over Traditional Funnels\n",
        "Traditional marketing funnels are linear and unsustainable [[Brian Balfour - Growth Loops]](src_brian_balfour_01). Loops create compounding reinvestment where the output of one cohort directly feeds the input of the next. **Sustainable growth is built on retention loops that compound over time.**\n",
        "### Your 3-Step Action Plan for Monday Morning:\n",
        "1. **Define Your PQL Threshold:** Identify the top 3 behavioral actions that predict 90-day retention.\n",
        "2. **Implement Guardrail Metrics:** Pair your primary activation metric with an uninstall or opt-out counter-metric [[Julie Zhuo - Metrics]](src_julie_zhuo_01).\n",
        "3. **Run a Team Pre-Mortem:** Assume your Q4 launch failed and list the existential risks before writing code."
    ]
    
    mock_text = "\n\n".join(sample_paragraphs)

    with patch.object(
        ship30_skill,
        "generate_essay",
        new=AsyncMock(return_value=(
            mock_text,
            [
                type("Citation", (), {"source_id": "src_elena_verna_01", "guest": "Elena Verna", "episode_title": "PLG", "topic": "PLG", "timestamp_str": "06:10", "snippet": "PLG definition", "source_reference": "EP58"})(),
                type("Citation", (), {"source_id": "src_shreyas_doshi_01", "guest": "Shreyas Doshi", "episode_title": "High Agency", "topic": "Strategy", "timestamp_str": "04:15", "snippet": "High agency definition", "source_reference": "EP42"})()
            ],
            GenerationResult(
                text=mock_text,
                input_tokens=850,
                output_tokens=420,
                total_tokens=1270,
                latency_ms=850.0,
                provider="ollama",
                model="llama3"
            )
        ))
    ):
        essay_text, citations, gen_res = await ship30_skill.generate_essay(
            topic="Why Most Startups Fail at Product-Led Growth (PLG)"
        )

        assert "# The PLG Illusion" in essay_text
        assert "**They are completely wrong.**" in essay_text
        assert "Elena Verna" in citations[0].guest
        assert "Shreyas Doshi" in citations[1].guest
        assert "3-Step Action Plan" in essay_text
        assert gen_res.total_tokens == 1270
