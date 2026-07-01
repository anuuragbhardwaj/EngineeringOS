"""Conversation routing tests."""

from orchestrator.conversation.router import ConversationRouter


def test_conversation_reuse_and_reset() -> None:
    router = ConversationRouter()
    c1 = router.resolve("p", "pm", "requirements")
    c2 = router.resolve("p", "pm", "requirements", reuse=True)
    assert c1 == c2

    c3 = router.reset("p", "pm", "requirements")
    assert c3 != c1


def test_conversation_branch() -> None:
    router = ConversationRouter()
    main = router.resolve("p", "ba", "specification")
    branch = router.branch("p", "ba", "specification", "rework")
    assert branch != main
