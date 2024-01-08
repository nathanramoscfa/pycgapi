# Contributing to CoinGeckoAPI

## Introduction

Thank you for considering contributing to CoinGeckoAPI! We welcome contributions from everyone and value your input and effort. This document provides guidelines to help you contribute effectively and ensure a smooth collaboration process.

## Getting Started

1. **Fork and Clone the Repository**: Start by forking the main repository and cloning your fork to your local machine.

    ```bash
    git clone https://github.com/your-username/coingeckoapi.git
    cd coingeckoapi
    ```

2. **Set Up Your Environment**: Make sure you have Python installed and set up a virtual environment. Install the development dependencies.

    ```bash
    python -m venv venv
    source venv/bin/activate  # For Linux/Mac
    venv\Scripts\activate  # For Windows
    pip install -r requirements_dev.txt
    ```

3. **Create a New Branch**: Create a new branch for your work.

    ```bash
    git checkout -b your-feature-branch
    ```

## Making Contributions

1. **Choose an Issue**: Look for open issues on GitHub. If you're new, look for issues tagged with "good first issue" 
   or "help wanted".

2. **Discuss Your Approach**: Before you start coding, it’s a good idea to discuss your approach. You can do this by 
   commenting on the issue you are planning to work on or creating a new issue to discuss your idea.

3. **Write Your Code**: Ensure your code adheres to the existing style of the project to maintain readability and 
   consistency.

4. **Write Tests**: If you add new features or fix bugs, write tests to cover your changes. Ensure all tests pass 
   before submitting your pull request.

5. **Document Your Changes**: Update the documentation if necessary. Include information about your changes, new 
   features, or any other relevant information for end-users.

6. **Commit Your Changes**: Use clear and concise commit messages, following best practices. Each commit should 
   represent a logical change.

    ```bash
    git add .
    git commit -m "Your detailed commit message"
    ```

7. **Push to Your Fork**: Push your changes to your fork on GitHub.

    ```bash
    git push origin your-feature-branch
    ```

8. **Create a Pull Request**: Go to the original `coingeckoapi` repository and create a pull request from your fork. 
   Provide a clear description in your pull request explaining your changes.

## After Submission

1. **Respond to Feedback**: Once you've submitted your pull request, the maintainers will review your changes. Be 
   responsive to feedback and make any necessary adjustments.

2. **Pull Request Merging**: Once your pull request is approved, a maintainer will merge it into the main repository.

## Questions or Issues?

If you have questions or encounter any issues, feel free to open an issue on GitHub or contact the maintainers directly.

Thank you for contributing to CoinGeckoAPI! Your efforts help make this project better for everyone.
