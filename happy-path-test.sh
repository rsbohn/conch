# Bytes → CAS → bytes
echo -n "abc" | conch put | tee /tmp/ref.txt
REF=$(cat /tmp/ref.txt)
conch get "$REF"  # prints: abc

# Shell capture
MAN=$(conch sh -c "echo hi")
echo "$MAN" | grep -q '^cas://blake3/'

# Python capture
PY=$(conch py -c "print(2+2)")
echo "$PY" | grep -q '^cas://blake3/'

# Pins
conch pin "$MAN" --tag "run/$(date +%F)"
conch ls | grep -q "run/"
