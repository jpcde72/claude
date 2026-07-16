from app.services.geo.analysis import TermAnalysis
from app.services.geo.insights import TRACKS, TRUST_PILLARS, generate_insights


def _analysis(term, surface="gemini", **kwargs):
    defaults = dict(mentioned=True, mention_count=1, sentiment_label="neutral")
    defaults.update(kwargs)
    return TermAnalysis(term=term, surface=surface, **defaults)


def test_invisible_terms_produce_p0_content_rec():
    analyses = [
        _analysis("best tents", mentioned=False, mention_count=0,
                  sentiment_label="not_mentioned"),
        _analysis("acme reviews", cited=True),
    ]
    recs = generate_insights(analyses, "Acme", "acme.com")
    content_recs = [r for r in recs if r.track == "content" and r.priority == "P0"]
    assert content_recs
    assert "best tents" in content_recs[0].affected_terms


def test_mentioned_uncited_produces_scripting_rec_with_snippet():
    analyses = [_analysis("best tents", cited=False)]
    recs = generate_insights(analyses, "Acme", "acme.com")
    scripting = [r for r in recs if r.track == "scripting"]
    assert scripting
    assert scripting[0].snippet and '"Organization"' in scripting[0].snippet


def test_negative_sentiment_produces_reputation_recs():
    analyses = [_analysis("acme reviews", sentiment_label="negative",
                          sentiment_score=-0.6, cited=True)]
    recs = generate_insights(analyses, "Acme", "acme.com")
    reputation = [r for r in recs if r.pillar == "reputation"]
    assert len(reputation) == 2
    assert any(r.snippet and '"FAQPage"' in r.snippet for r in reputation)


def test_transactional_terms_produce_pdp_recs():
    analyses = [_analysis("best tent to buy", cited=False)]
    recs = generate_insights(analyses, "Acme", "acme.com")
    pdp = [r for r in recs if r.track == "pdp"]
    assert pdp
    product = [r for r in recs if r.snippet and '"Product"' in r.snippet]
    assert product


def test_transactional_marker_does_not_match_inside_words():
    # "laptop" contains "top" but is not a transactional term by itself
    analyses = [_analysis("laptop stands", cited=True)]
    recs = generate_insights(analyses, "Acme", "acme.com")
    assert not [r for r in recs if r.track == "pdp"]


def test_share_of_voice_gap_produces_authority_rec():
    analyses = [_analysis("best tents", cited=True,
                          competitor_mentions={"TrailPro": 3})]
    recs = generate_insights(analyses, "Acme", "acme.com", ["TrailPro"])
    assert [r for r in recs if r.pillar == "authority"]


def test_cross_surface_gap_produces_consistency_rec():
    analyses = [
        _analysis("best tents", surface="gemini", cited=True),
        _analysis("best tents", surface="ai_overview", mentioned=False,
                  mention_count=0, sentiment_label="not_mentioned"),
    ]
    recs = generate_insights(analyses, "Acme", "acme.com")
    assert [r for r in recs if "cross-surface" in r.title.lower()
            or "Reconcile" in r.title]


def test_all_recs_use_known_pillars_tracks_and_are_priority_sorted():
    analyses = [
        _analysis("best tents to buy", mentioned=False, mention_count=0,
                  sentiment_label="not_mentioned"),
        _analysis("acme reviews", sentiment_label="negative", sentiment_score=-0.5),
        _analysis("tents comparison", cited=False,
                  competitor_mentions={"TrailPro": 2}, competitor_cited=["TrailPro"]),
    ]
    recs = generate_insights(analyses, "Acme", "acme.com", ["TrailPro"])
    assert recs
    for rec in recs:
        assert rec.pillar in TRUST_PILLARS
        assert rec.track in TRACKS
    priorities = [r.priority for r in recs]
    assert priorities == sorted(priorities)


def test_no_answers_no_recs():
    analyses = [_analysis("x", answered=False, mentioned=False,
                          mention_count=0, error="boom",
                          sentiment_label="not_mentioned")]
    assert generate_insights(analyses, "Acme") == []
