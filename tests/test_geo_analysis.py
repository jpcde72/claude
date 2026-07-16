from app.services.geo.analysis import analyze_response, extract_domain
from app.services.geo.providers import Citation, SurfaceResponse


def _resp(text, citations=None, ok=True, error=None):
    return SurfaceResponse(
        surface="gemini",
        term="best hiking boots",
        text=text,
        citations=citations or [],
        ok=ok,
        error=error,
    )


def test_detects_brand_mention_and_prominence():
    resp = _resp("Acme Outdoor makes the most reliable boots. Many hikers recommend Acme Outdoor.")
    a = analyze_response(resp, "Acme Outdoor")
    assert a.mentioned
    assert a.mention_count == 2
    assert a.prominence > 0.9  # mentioned at the very start
    assert "Acme Outdoor" in a.evidence


def test_brand_variant_without_space_is_matched():
    resp = _resp("AcmeOutdoor is a popular choice.")
    a = analyze_response(resp, "Acme Outdoor")
    assert a.mentioned


def test_no_false_positive_inside_words():
    resp = _resp("The acmeoutdoorsy trend is unrelated.")
    a = analyze_response(resp, "Acme Outdoor")
    assert not a.mentioned
    assert a.sentiment_label == "not_mentioned"


def test_citation_detection_matches_domain_and_subdomain():
    citations = [
        Citation(url="https://www.acmeoutdoor.com/boots", title="Boots"),
        Citation(url="https://blog.acmeoutdoor.com/guide", title="Guide"),
        Citation(url="https://en.wikipedia.org/wiki/Hiking", title="Hiking"),
    ]
    resp = _resp("Acme Outdoor is often cited.", citations=citations)
    a = analyze_response(resp, "Acme Outdoor", brand_domain="acmeoutdoor.com")
    assert a.cited
    assert "acmeoutdoor.com" in a.citation_domains
    assert "en.wikipedia.org" in a.citation_domains


def test_not_cited_when_only_third_parties():
    citations = [Citation(url="https://reddit.com/r/hiking", title="thread")]
    resp = _resp("Acme Outdoor gets mixed reviews.", citations=citations)
    a = analyze_response(resp, "Acme Outdoor", brand_domain="acmeoutdoor.com")
    assert not a.cited


def test_positive_sentiment():
    resp = _resp("Acme Outdoor is excellent, reliable, and widely recommended by experts.")
    a = analyze_response(resp, "Acme Outdoor")
    assert a.sentiment_score > 0
    assert a.sentiment_label == "positive"


def test_negative_sentiment():
    resp = _resp("Users say Acme Outdoor is unreliable and expensive, with many complaints.")
    a = analyze_response(resp, "Acme Outdoor")
    assert a.sentiment_score < 0
    assert a.sentiment_label == "negative"


def test_competitor_mentions_and_share_of_voice():
    resp = _resp("TrailPro leads the pack. TrailPro and Summit Gear beat Acme Outdoor here.")
    a = analyze_response(
        resp, "Acme Outdoor", competitors=["TrailPro", "Summit Gear"]
    )
    assert a.competitor_mentions == {"TrailPro": 2, "Summit Gear": 1}
    assert a.share_of_voice == 0.25


def test_provider_error_marks_unanswered():
    resp = _resp("", ok=False, error="boom")
    a = analyze_response(resp, "Acme Outdoor")
    assert not a.answered
    assert a.error == "boom"


def test_extract_domain_strips_www():
    assert extract_domain("https://www.example.com/x") == "example.com"
    assert extract_domain("https://sub.example.com/x") == "sub.example.com"
