from mythron.capabilities import Capability, CapabilityRegistry


def test_register_and_get_capability():
    registry = CapabilityRegistry()

    capability = Capability(
        name="browser",
        description="Controlled browser interaction",
        category="browser",
    )

    registry.register(capability)

    assert registry.contains("browser")
    assert registry.get("browser") == capability


def test_list_and_enabled_capabilities():
    registry = CapabilityRegistry()

    registry.register(
        Capability(
            name="browser",
            description="Controlled browser interaction",
            category="browser",
        )
    )

    registry.register(
        Capability(
            name="disabled_test",
            description="Disabled capability for testing",
            category="test",
            enabled=False,
        )
    )

    assert len(registry.list_all()) == 2
    assert [c.name for c in registry.enabled()] == ["browser"]


def test_empty_capability_name_is_rejected():
    registry = CapabilityRegistry()

    try:
        registry.register(
            Capability(
                name="",
                description="Invalid capability",
                category="test",
            )
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "name" in str(exc).lower()


def test_unknown_capability_returns_none():
    registry = CapabilityRegistry()

    assert registry.get("does_not_exist") is None
    assert not registry.contains("does_not_exist")
