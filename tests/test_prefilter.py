import pytest
from core.models import RawSignal
from scorer.prefilter import passes


def sig(title="", body=""):
    return RawSignal(source="test", url="http://x.com", title=title, body=body, ts=0)


def test_strong_intent_passes():
    s = sig("Looking for a CI/CD tool recommendation", "We are switching from Jenkins and need something modern")
    assert passes(s)


def test_pure_spam_fails():
    s = sig("Buy now!", "Click here for amazing deals on sunglasses")
    assert not passes(s)


def test_negation_fails():
    s = sig("Not looking for a new tool", "We already have a solution for our CI/CD pipeline")
    assert not passes(s)


def test_too_short_fails():
    s = sig("help", "hi")
    assert not passes(s)


def test_no_vertical_hint_fails():
    s = sig("Looking for recommendations", "I need help with my personal life choices today")
    assert not passes(s)


def test_alternative_intent_passes():
    s = sig(
        "Alternative to Datadog for monitoring",
        "We are tired of Datadog pricing and looking for a cheaper cloud monitoring solution"
    )
    assert passes(s)


def test_hiring_signal_passes():
    s = sig(
        "Hiring DevOps engineers",
        "Our startup is hiring DevOps engineers to help with our AWS infrastructure and Kubernetes deployment pipeline"
    )
    assert passes(s)
