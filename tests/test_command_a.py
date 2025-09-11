from conch.sam import Sam

buffer = "123\n456\n789\n".splitlines()
app = Sam()

def test_1a():
    b1, dot = app.exec("1ahello", buffer, (0,0))
    assert b1 == ["123", "hello", "456", "789"]
    assert dot == (1,1)

    b1, dot = app.exec("1a/hello/", buffer, (0,0))
    assert b1 == ["123", "hello", "456", "789"]
    assert dot == (1,2)
    b2, dot = app.exec(".d", b1, dot)
    assert b2 == ["123", "456", "789"]
    assert dot == (1,1)
