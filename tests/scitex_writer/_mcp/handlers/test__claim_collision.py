#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Two claim IDs must never collapse onto one LaTeX macro.

THE BUG. Macro names are built by `_sanitize_id`, which strips every
non-alphanumeric character: `group-a-effect` and `group_a_effect` both become
`groupaeffect`. The renderer emits one `\\@namedef` per claim, and `\\@namedef`
is `\\def` — the second definition silently replaces the first. Both `\\vclaim`
calls then expand to the LAST claim's value.

Reproduced against the real renderer before this guard existed (2026-07-17):

    render_claims success: True
    \\@namedef for v@claim@groupaeffect@nature: 2 definitions
        defines value -> 111
        defines value -> 999

So `\\vclaim{group-a-effect}` printed 999 — the OTHER claim's value — into the
manuscript, with no warning, from a renderer reporting success. That is the most
severe form of this family: not a wrong version string in metadata, but a wrong
NUMBER in a published scientific paper.

There is no legitimate collision: two distinct claims sharing a macro is always
a defect, so it is a hard refusal rather than a warning.

The decision functions are pure, so these run on real values with no mock and no
monkeypatch (PA-306 / STX-NM002).
"""

from scitex_writer._mcp.handlers._claim_format import (
    _sanitize_id,
    describe_sanitize_collisions,
    find_sanitize_collisions,
)

# The exact pair that reproduced the bug.
COLLIDING = ["group-a-effect", "group_a_effect"]


class TestCollisionIsDetected:
    def test_ids_differing_only_in_punctuation_collide(self):
        # Arrange
        ids = COLLIDING

        # Act
        collisions = find_sanitize_collisions(ids)

        # Assert
        assert collisions == {"groupaeffect": COLLIDING}

    def test_the_collision_is_real_not_hypothetical(self):
        # Arrange: both really do sanitise to one macro name.
        ids = COLLIDING

        # Act
        sanitised = {_sanitize_id(i) for i in ids}

        # Assert
        assert len(sanitised) == 1

    def test_three_way_collision_is_reported_as_one_group(self):
        # Arrange
        ids = ["a-b", "a_b", "a.b"]

        # Act
        collisions = find_sanitize_collisions(ids)

        # Assert
        assert collisions == {"ab": ids}


class TestDistinctIdsAreNotFlagged:
    def test_genuinely_distinct_ids_do_not_collide(self):
        # Arrange
        ids = ["group-a-effect", "group-b-effect"]

        # Act
        collisions = find_sanitize_collisions(ids)

        # Assert
        assert collisions == {}

    def test_a_single_claim_never_collides_with_itself(self):
        # Arrange
        ids = ["group-a-effect"]

        # Act
        collisions = find_sanitize_collisions(ids)

        # Assert
        assert collisions == {}

    def test_no_claims_is_not_a_collision(self):
        # Arrange
        ids = []

        # Act
        collisions = find_sanitize_collisions(ids)

        # Assert
        assert collisions == {}


class TestRefusalMessage:
    def test_message_names_every_colliding_id(self):
        # Arrange
        collisions = {"groupaeffect": COLLIDING}

        # Act
        message = describe_sanitize_collisions(collisions)

        # Assert
        assert "group-a-effect, group_a_effect" in message

    def test_message_names_the_shared_macro(self):
        # Arrange
        collisions = {"groupaeffect": COLLIDING}

        # Act
        message = describe_sanitize_collisions(collisions)

        # Assert
        assert "\\v@claim@groupaeffect@*" in message

    def test_message_states_the_stake_a_wrong_number(self):
        # Arrange: a reader must know a VALUE is at risk, not just a name.
        collisions = {"groupaeffect": COLLIDING}

        # Act
        message = describe_sanitize_collisions(collisions)

        # Assert
        assert "wrong number" in message

    def test_message_hands_back_an_actionable_remedy(self):
        # Arrange
        collisions = {"groupaeffect": COLLIDING}

        # Act
        message = describe_sanitize_collisions(collisions)

        # Assert
        assert "Rename the claim IDs" in message
