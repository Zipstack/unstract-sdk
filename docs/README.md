# Documentation generation

[Lazydocs](https://github.com/ml-tooling/lazydocs) is used for markdown generation from the Google style python docstrings.

Install this dependency along with the SDK using
```
pip install -e ".[docs]"
```

Execute the below command from [sdks](/sdks/) in order to generate the markdown files into [API reference](/sdks/docs/site/docs/API%20Reference/).
```
lazydocs src/unstract/sdk \
--output-path ./docs/site/docs/API\ Reference/ \
--src-base-url https://github.com/Zipstack/unstract/tree/development
```

**NOTE:** There exists issues with lazydocs' generation and all image tags in the generated markdown need to be removed for
the being. A find and replace with the regex of `<a href=.*` into an empty string might help.

Test by building the site with the following command
```
npm run serve -- --build --port 4500 --host 127.0.0.1
```
