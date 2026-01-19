# Publishing Guide

This document describes how to publish `yomemoai-mcp` to PyPI so that users can install it using `uvx yomemoai-mcp`.

## Prerequisites

1. **PyPI Account**: Create an account at [PyPI](https://pypi.org/) if you don't have one
2. **TestPyPI Account** (recommended for testing): Create an account at [TestPyPI](https://test.pypi.org/)
3. **API Token**: You'll need an API token to publish packages

### Important: TestPyPI vs PyPI Accounts

**TestPyPI and PyPI are separate systems**, but you can use the **same username and password** for both:

- **Same credentials work**: If you register on TestPyPI, you can use the same username and password to register on PyPI
- **Separate accounts**: They are technically separate accounts, but sharing credentials is common and recommended
- **Email conflicts**: If you get an "email already in use" error on PyPI:
  - You may have already registered on PyPI before (check your email for activation links)
  - Or someone else is using that email (unlikely but possible)
  - **Solution**: Try password reset on PyPI using the same email, or use a different email

**Recommended approach**: Register on both TestPyPI and PyPI using the same username and password for consistency.

## Step 1: Create API Token

1. Log in to [PyPI](https://pypi.org/)
2. Go to **Account settings** → **API tokens**
3. Click **Add API token**
4. Choose scope:
   - **Entire account**: Can publish any package (recommended for personal projects)
   - **Project-specific**: Limited to a specific package
5. **Important**: Copy the token immediately - it's only shown once!
   - Format: `pypi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

## Step 2: Configure Authentication

### Option A: Using Environment Variable (Recommended)

```bash
export UV_PUBLISH_TOKEN=pypi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Option B: Using uv's Credential Store

uv will prompt for credentials when you run `uv publish` for the first time.

## Step 3: Build the Package

Before publishing, build the package to ensure everything is correct:

```bash
cd python-yomemo-mcp
uv build
```

This will create a `dist/` directory containing:

- `yomemoai_mcp-0.1.0-py3-none-any.whl` (wheel distribution)
- `yomemoai-mcp-0.1.0.tar.gz` (source distribution)

## Step 4: Test on TestPyPI (Recommended)

Before publishing to the real PyPI, test on TestPyPI:

### 4.1 Create TestPyPI API Token

1. Log in to [TestPyPI](https://test.pypi.org/)
2. Create an API token (same process as PyPI)
3. Export the token:
   ```bash
   export UV_PUBLISH_TOKEN=pypi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### 4.2 Publish to TestPyPI

```bash
uv publish --publish-url https://test.pypi.org/legacy/
```

### 4.3 Test Installation

Test that the package can be installed and run:

**Important**: TestPyPI may not have all dependencies. Use `--extra-index-url` to fetch dependencies from PyPI while getting the package from TestPyPI:

```bash
# Test installation from TestPyPI (dependencies from PyPI)
uvx --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ yomemoai-mcp --help

# Or test in a clean environment
uv venv test-env
source test-env/bin/activate  # On Windows: test-env\Scripts\activate
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ yomemoai-mcp
yomemoai-mcp --help
```

**Note**: The `--extra-index-url` flag tells the package manager to also check PyPI for dependencies that might not be available on TestPyPI.

## Step 5: Publish to PyPI

Once testing is successful, publish to the real PyPI:

### 5.1 Set Production API Token

```bash
export UV_PUBLISH_TOKEN=pypi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 5.2 Publish

```bash
uv publish
```

Or explicitly specify the URL:

```bash
uv publish --publish-url https://upload.pypi.org/legacy/
```

## Step 6: Verify Publication

After publishing, verify the package is available:

### 6.1 Check Package on PyPI

Visit: https://pypi.org/project/yomemoai-mcp/

### 6.2 Test Installation

```bash
# Test with uvx
uvx yomemoai-mcp --help

# Or install directly
pip install yomemoai-mcp
yomemoai-mcp --help
```

### 6.3 Check Package Metadata

```bash
curl https://pypi.org/pypi/yomemoai-mcp/json | jq
```

## Updating the Package

When you need to publish a new version:

1. **Update version** in `pyproject.toml`:

   ```toml
   version = "0.1.1"  # or 0.2.0, 1.0.0, etc.
   ```

2. **Update CHANGELOG** (if you maintain one)

3. **Build and publish**:
   ```bash
   uv build
   uv publish
   ```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.1.0): New features, backward compatible
- **PATCH** (0.1.1): Bug fixes, backward compatible

## Troubleshooting

### Error: "Package already exists"

- If you're updating an existing package, make sure to increment the version number
- If the package name is taken, you'll need to choose a different name

### Error: "Invalid credentials"

- Check that your API token is correct
- Make sure you're using the right token (TestPyPI vs PyPI)
- Tokens expire after a period of inactivity - create a new one if needed

### Error: "File already exists"

- The version you're trying to publish already exists
- Increment the version number in `pyproject.toml`

### Package not found after publishing

- Wait a few minutes - PyPI indexing can take time
- Check the package name is correct: `yomemoai-mcp`
- Verify the package is published: https://pypi.org/project/yomemoai-mcp/

## Security Notes

- **Never commit** API tokens to version control
- Use environment variables or credential stores
- Rotate tokens periodically
- Use project-specific tokens when possible (more secure than account-wide tokens)

## Additional Resources

- [PyPI Documentation](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Python Packaging User Guide](https://packaging.python.org/)
