from conch.sam import Sam

app = Sam()

def make_buffer():
    return "123\n456\n789\n".splitlines()

def test_Nd():
    buffer = make_buffer()
    b1, dot = app.exec("1d", buffer, (0,0))
    assert b1 == ["456", "789"]
    assert dot == (0,0)

    b2, dot = app.exec("2d", buffer, (0,0))
    assert b2 == ["123", "789"]
    assert dot == (1,1)
    
    b3, dot = app.exec("3d", buffer, (0,0))
    assert b3 == ["123", "456"]
    assert dot == (2,2)

def test_Nd_out_of_range():
    buffer = make_buffer()
    b4, dot = app.exec("4d", buffer, (0,0))
    assert b4 == ["123", "456", "789"]
    assert dot == (3,3)

def test_MNd():
    buffer = make_buffer()
    b1, dot = app.exec("1,2d", buffer, (0,0))
    assert b1 == ["789"]
    assert dot == (0,0)

    b2, dot = app.exec("2,3d", buffer, (0,0))
    assert b2 == ["123"]
    assert dot == (0,0)

    b3, dot = app.exec("1,3d", buffer, (0,0))
    assert b3 == []
    assert dot == (0,0)