# Crash Signature Service

A service to generate a crash signature based on a stack trace frames list.

It works with several languages (including C/C++ and Java at the moment), and is highly configurable.

## Try it

```bash
$ http --json post 'https://crash-signature-service.herokuapp.com/sign?lang=c' \
frames:='["NtWaitForMultipleObjects", "WaitForMultipleObjectsEx", \
"WaitForMultipleObjectsExImplementation", "RealMsgWaitForMultipleObjectsEx", \
"MsgWaitForMultipleObjects", "F_1152915508___________________________________", \
"F2166389_____________________________________________________________________"]'
```

Returns:

```json
{
    "language": "c",
    "notes": [],
    "signature": "WaitForMultipleObjectsEx | MsgWaitForMultipleObjects | F_1152915508___________________________________"
}
```

## Development

### Installing

Create a Python virtualenv:

```bash
$ virtualenv env
```

Update pip to the latest version (version >8 is needed to use secure hashes):

```bash
$ pip install -U pip
```

Then install all dependencies:

```bash
$ pip install --require-hashes -r requirements.txt
```

### Running locally

This service uses [gunicorn](http://gunicorn.org/) to expose itself on the Web.

```bash
$ make run
```

### Tests

Tests run using [py.test](http://pytest.org/).

```bash
$ make test
```
