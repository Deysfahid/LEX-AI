import json
import os
import asyncio
import httpx
from typing import AsyncGenerator

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "llama-3.3-70b-versatile"

STEP_LABELS = [
    "Classifying case type...",
    "Summarizing the case...",
    "Extracting legal issues...",
    "Identifying parties...",
    "Building timeline...",
    "Calculating risk scores...",
    "Finding evidence gaps...",
    "Generating recommendations...",
    "Searching similar cases...",
]

STEP_ICONS = ["\U0001f50d", "\U0001f4dd", "\u2696\ufe0f", "\U0001f465", "\U0001f4c5", "\U0001f3af", "\U0001f50e", "\U0001f4a1", "\U0001f4da"]


async def call_groq(system_prompt: str, user_prompt: str) -> str:
    """Make a call to Groq API with retry logic for rate limits."""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 2048,
    }
    max_retries = 5
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(f"{GROQ_BASE_URL}/chat/completions", json=payload, headers=headers)
                if resp.status_code == 429:
                    wait = 5 * (attempt + 1)
                    print(f"Rate limited. Waiting {wait}s before retry {attempt + 1}/{max_retries}...")
                    await asyncio.sleep(wait)
                    continue
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429 and attempt < max_retries - 1:
                wait = 5 * (attempt + 1)
                print(f"Rate limited. Waiting {wait}s before retry {attempt + 1}/{max_retries}...")
                await asyncio.sleep(wait)
                continue
            raise
        except Exception:
            if attempt < max_retries - 1:
                await asyncio.sleep(3)
                continue
            raise
    raise Exception("Groq API rate limit exceeded. Please wait a minute and try again.")


def extract_json(text: str) -> dict:
    """Extract JSON from LLM response text that may contain markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        return json.loads(text[start:end + 1])
    return json.loads(text)


def extract_json_array(text: str) -> list:
    """Extract JSON array from LLM response text."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1:
        return json.loads(text[start:end + 1])
    return json.loads(text)


async def run_agent(document_text: str, progress_callback=None) -> dict:
    """Run the 9-step agentic analysis pipeline using 3 combined API calls."""

    max_chars = 30000
    if len(document_text) > max_chars:
        document_text = document_text[:max_chars]

    results = {}

    # STEP 1-2: Classify + Summarize (combined)
    if progress_callback:
        await progress_callback(0)
    resp = await call_groq(
        "You are a legal case analyst. Respond with ONLY a JSON object.",
        f"""Analyze this legal document and return ONLY this JSON:
{{"classification": {{"case_type": "<Criminal|Civil|Contract|Family|Property|Corporate>", "confidence": <0-100>}}, "summary": {{"summary": "<plain English summary>", "what_happened": "<what happened>", "parties_involved": "<who is involved>", "dispute": "<what is being disputed>"}}}}

Document:
{document_text}"""
    )
    parsed = extract_json(resp)
    results["classification"] = parsed.get("classification", {})
    if progress_callback:
        await progress_callback(1)
    results["summary"] = parsed.get("summary", {})

    # STEP 3-4: Key Issues + Parties (combined)
    if progress_callback:
        await progress_callback(2)
    resp = await call_groq(
        "You are a legal case analyst. Respond with ONLY a JSON object.",
        f"""Extract key issues and parties from this document. Return ONLY this JSON:
{{"key_issues": {{"issues": ["issue1", "issue2", "issue3"]}}, "parties": {{"plaintiff": "<name>", "defendant": "<name>", "lawyers": ["name1", "name2"], "judge": "<name or 'Not mentioned'>"}}}}

Document:
{document_text}"""
    )
    parsed = extract_json(resp)
    results["key_issues"] = parsed.get("key_issues", {})
    if progress_callback:
        await progress_callback(3)
    results["parties"] = parsed.get("parties", {})

    await asyncio.sleep(2)

    # STEP 5-6: Timeline + Risk Analysis (combined)
    if progress_callback:
        await progress_callback(4)
    resp = await call_groq(
        "You are a legal case analyst. Respond with ONLY a JSON object.",
        f"""Extract timeline and analyze risk from this document. Return ONLY this JSON:
{{"timeline": {{"timeline": [{{"date": "DD-MM-YYYY or approximate", "event": "description"}}]}}, "risk_analysis": {{"plaintiff_risk": {{"score": <0-100>, "reasoning": "<reasoning>"}}, "defendant_risk": {{"score": <0-100>, "reasoning": "<reasoning>"}}}}}}

Document:
{document_text}"""
    )
    parsed = extract_json(resp)
    results["timeline"] = parsed.get("timeline", {})
    if progress_callback:
        await progress_callback(5)
    results["risk_analysis"] = parsed.get("risk_analysis", {})

    await asyncio.sleep(2)

    # STEP 7-8: Missing Evidence + Recommendations (combined)
    if progress_callback:
        await progress_callback(6)
    resp = await call_groq(
        "You are a legal case analyst. Respond with ONLY a JSON object.",
        f"""Identify missing evidence and provide recommendations. Return ONLY this JSON:
{{"missing_evidence": {{"missing_documents": ["doc1"], "weak_arguments": ["arg1"], "gaps": ["gap1"]}}, "recommendations": {{"recommendations": ["rec1", "rec2", "rec3", "rec4", "rec5"]}}}}

Document:
{document_text}"""
    )
    parsed = extract_json(resp)
    results["missing_evidence"] = parsed.get("missing_evidence", {})
    if progress_callback:
        await progress_callback(7)
    results["recommendations"] = parsed.get("recommendations", {})

    await asyncio.sleep(2)

    # STEP 9: Similar Cases
    if progress_callback:
        await progress_callback(8)
    resp = await call_groq(
        "You are a legal researcher with knowledge of landmark Indian court cases. Respond with ONLY a JSON object.",
        f"""Find 3 similar landmark Indian court cases relevant to this document. Return ONLY this JSON:
{{"similar_cases": [{{"name": "<case name>", "year": "<year>", "outcome": "<outcome summary>", "relevance": "<why it is relevant>"}}]}}

Document:
{document_text}"""
    )
    results["similar_cases"] = extract_json(resp)

    return results


async def run_agent_stream(document_text: str) -> AsyncGenerator[str, None]:
    """Run the agent and yield SSE-formatted progress events."""

    async def on_step(idx: int):
        icon = STEP_ICONS[idx] if idx < len(STEP_ICONS) else "\u2699\ufe0f"
        label = STEP_LABELS[idx] if idx < len(STEP_LABELS) else "Processing..."
        return json.dumps({"step": idx + 1, "total": 9, "label": label, "icon": icon})

    yield f"data: {json.dumps({'step': 0, 'total': 9, 'label': 'Starting analysis...', 'icon': '\u2699\ufe0f'})}\n\n"

    result = await run_agent(document_text, progress_callback=on_step)

    yield f"data: {json.dumps({'step': 9, 'total': 9, 'label': 'Analysis complete!', 'icon': '\u2705', 'result': result})}\n\n"


def get_demo_data() -> dict:
    """Return realistic demo analysis data for an Indian property dispute case."""
    return {
        "classification": {
            "case_type": "Property",
            "confidence": 95
        },
        "summary": {
            "summary": "This is a property dispute case concerning the ownership of a 2-acre agricultural land parcel in Village Rampur, District Ghaziabad, Uttar Pradesh. The plaintiff claims ancestral ownership based on a 1972 revenue record, while the defendant purchased the same property in 2018 through a registered sale deed.",
            "what_happened": "The plaintiff discovered in 2021 that the defendant had obtained a sale deed for property the plaintiff considers ancestral. The defendant claims he purchased the property from an individual who had a valid mutation entry in revenue records. The plaintiff filed a suit for declaration of title and cancellation of the sale deed.",
            "parties_involved": "Plaintiff: Mr. Rajesh Kumar Sharma (landowner). Defendant: Mr. Vikram Singh (purchaser). Third Party: Mr. Sunil Verma (person who sold to defendant).",
            "dispute": "Whether the sale deed executed in favour of the defendant is valid when the original title holder (plaintiff) never consented to the sale, and whether the mutation entry in favour of the third party was obtained through fraud."
        },
        "key_issues": {
            "issues": [
                "Whether the mutation entry dated 15-03-2017 in favour of Sunil Verma is valid and legal",
                "Whether the sale deed dated 10-08-2018 executed by Sunil Verma in favour of Vikram Singh is enforceable",
                "Whether the original land ownership by Rajesh Kumar Sharma under 1972 revenue records is established",
                "Whether the defendant exercised due diligence before purchasing the property",
                "Whether the suit is barred by limitation under Article 59 of the Limitation Act, 1963",
                "Whether the plaintiff is entitled to mesne profits for the period of dispossession"
            ]
        },
        "parties": {
            "plaintiff": "Mr. Rajesh Kumar Sharma",
            "defendant": "Mr. Vikram Singh",
            "lawyers": ["Advocate Meera Joshi (for Plaintiff)", "Advocate Arjun Kapoor (for Defendant)"],
            "judge": "Hon'ble Justice S.K. Mishra, District Judge, Ghaziabad"
        },
        "timeline": {
            "timeline": [
                {"date": "12-05-1972", "event": "Original revenue record (Khatauni) established in name of plaintiff's grandfather, Late Shri Hari Sharma"},
                {"date": "22-11-1988", "event": "Property inherited by plaintiff's father, Late Shri Prem Sharma, after grandfather's death"},
                {"date": "05-09-2005", "event": "Property inherited by plaintiff Rajesh Kumar Sharma after father's death"},
                {"date": "15-03-2017", "event": "Mutation entry entered in favour of Sunil Verma based on alleged oral gift deed"},
                {"date": "10-08-2018", "event": "Sale deed executed between Sunil Verma and defendant Vikram Singh for Rs. 45,00,000"},
                {"date": "03-01-2021", "event": "Plaintiff discovers mutation and sale through village patwari during harvest inspection"},
                {"date": "28-02-2021", "event": "Plaintiff files legal notice to defendant and third party"},
                {"date": "15-06-2021", "event": "Civil suit filed in District Court, Ghaziabad"},
                {"date": "10-09-2021", "event": "Interim injunction granted restraining defendant from alienating property"},
                {"date": "05-03-2022", "event": "Defendant files written statement contesting plaintiff's title"}
            ]
        },
        "risk_analysis": {
            "plaintiff_risk": {
                "score": 35,
                "reasoning": "The plaintiff has strong documentary evidence including original 1972 Khatauni and chain of inheritance documents. However, the delay in discovering the mutation (4 years) and the gap in not checking revenue records regularly may weaken the claim. The limitation period under Article 59 (3 years from when fraud was discovered) appears to be within time. The plaintiff has a 65% probability of success."
            },
            "defendant_risk": {
                "score": 72,
                "reasoning": "The defendant faces significant risk as the chain of title has a critical defect. The mutation in favour of Sunil Verma was based on an alleged oral gift deed which has no documentary evidence. The defendant's due diligence is questionable as he did not verify the original revenue records dating back to 1972. Under Section 54 of the Transfer of Property Act, the buyer must exercise reasonable care. The defendant may lose both the property and the purchase price of Rs. 45 lakhs."
            }
        },
        "missing_evidence": {
            "missing_documents": [
                "Original oral gift deed allegedly executed by plaintiff's father in favour of Sunil Verma",
                "Consent of all legal heirs of Late Shri Prem Sharma for any transfer",
                "Due diligence report or title search conducted by defendant before purchase",
                "No Objection Certificate from Revenue Department for mutation",
                "Witness statements for the alleged oral gift"
            ],
            "weak_arguments": [
                "Defendant's claim of being a bona fide purchaser is weak due to inadequate title verification",
                "Sunil Verma has not been examined as a witness and his whereabouts are unknown",
                "The mutation entry does not have supporting affidavit from the transferor",
                "No revenue court order was obtained for the mutation — it was done administratively"
            ],
            "gaps": [
                "The period between mutation (2017) and discovery (2021) needs explanation to avoid limitation defence",
                "No valuation report was obtained for the suit property",
                "Defendant has not filed any counter-claim for refund of purchase price"
            ]
        },
        "recommendations": {
            "recommendations": [
                "File an application under Order 39 Rule 1 & 2 CPC to continue the interim injunction and seek attachment of the property pending disposal",
                "Summon Sunil Verma as a necessary party under Order 1 Rule 10 CPC and examine him on the alleged oral gift deed",
                "Obtain certified copies of all revenue records from 1972 to present from the Tehsildar's office to establish a clear chain of title",
                "File a criminal complaint under Sections 420 (cheating) and 467 (forgery) of the IPC against Sunil Verma for the fraudulent mutation",
                "Request the court to appoint a Local Commissioner under Order 26 Rule 9 CPC to inspect the land and prepare a map identifying boundaries as per 1972 records"
            ]
        },
        "similar_cases": {
            "similar_cases": [
                {
                    "name": "Suraj Lamp & Industries Pvt. Ltd. vs State of Haryana",
                    "year": "2012",
                    "outcome": "The Supreme Court held that sale through General Power of Attorney (GPA) and oral agreements are not valid modes of transfer. Only registered sale deeds convey title. The defendant's reliance on a chain involving an oral gift deed falls under this principle.",
                    "relevance": "Directly relevant as the mutation was based on an alleged oral gift which is not a valid mode of property transfer under Indian law."
                },
                {
                    "name": "Rambhau vs Narayan (2003) 4 SCC 326",
                    "year": "2003",
                    "outcome": "The Supreme Court held that a bona fide purchaser for value without notice of prior claims is protected, but the burden of proving bona fide and due diligence is on the purchaser.",
                    "relevance": "The defendant claims bona fide purchaser status but failed to conduct proper title verification, making this defence weak."
                },
                {
                    "name": "Hungerford Investment Trust Ltd vs Haridas Mundhra",
                    "year": "1972",
                    "outcome": "The Supreme Court ruled that when title is disputed, the court must trace the entire chain of ownership and verify each link. A defect in any link breaks the chain and renders subsequent transfers void.",
                    "relevance": "The break in the chain of title from the plaintiff to Sunil Verma (via unsubstantiated oral gift) makes all subsequent transfers void."
                }
            ]
        }
    }
