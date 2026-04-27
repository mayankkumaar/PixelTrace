from app.services.scheduler import generate_embedding_plan


def test_guaranteed_window_sampling():
    frame_count = 300
    window = 30
    plan = generate_embedding_plan(frame_count=frame_count, window_size=window, random_probability=0.0)

    assert len(plan) > 0
    prev = -1
    for idx in plan:
        assert idx - prev <= window
        prev = idx
