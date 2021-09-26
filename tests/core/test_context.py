from unittest.mock import sentinel

from preacher.core.context import Context, closed_context


def test_context():
    context = Context(foo="bar")
    assert list(context) == ["foo"]
    assert context != {"foo": "bar"}
    assert context == Context(foo="bar")


def test_closed_context():
    context = Context(
        control=sentinel.control,
        normal=sentinel.normal_out_of_context,
        deleted=sentinel.deleted_out_of_context,
        overwritten=sentinel.overwritten_out_of_context,
    )

    with closed_context(
        context,
        normal=sentinel.normal_in_context,
        deleted=sentinel.deleted_in_context,
        overwritten=sentinel.overwritten_in_context,
        contextual=sentinel.contextual,
    ) as context:
        assert context["control"] is sentinel.control
        assert context["normal"] is sentinel.normal_in_context
        assert context["deleted"] is sentinel.deleted_in_context
        assert context["overwritten"] is sentinel.overwritten_in_context
        assert context["contextual"] is sentinel.contextual

        del context["deleted"]
        context["overwritten"] = sentinel.overwritten_new
        context["not_contextual"] = sentinel.not_contextual

    assert context["control"] is sentinel.control
    assert context["normal"] is sentinel.normal_out_of_context
    assert context["deleted"] is sentinel.deleted_out_of_context
    assert context["overwritten"] is sentinel.overwritten_out_of_context
    assert context["not_contextual"] is sentinel.not_contextual
    assert "contextual" not in context
