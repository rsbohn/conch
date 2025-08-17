# 2025-08-16 Plan for ai

## MVP

Use the `anthropic` package.
The key can be read from the filename provided in $env:keyfile.
Start with a simple query-response.
In any mode, the prefix /ai signals that a prompt follows (the rest of the input line).
Prepare and send the request to Claude 3.5 haiku.
Extract the text response and print it.
Handle any errors appropriately.

### Fail Fast

If the keyfile is not available print the command to set it, then exit.

    $env:keyfile = ...
    export keyfile=...

The user can copy-paste the relevant command, add the actual value, and execute it.