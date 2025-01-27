# Security Policy

## Supported Versions

Currently supported versions of fibery-client with security updates:

| Version | Supported          |
|---------|-------------------|
| 0.1.x   | :white_check_mark: |

## Security Considerations

### API Token Security
- Never commit your Fibery API token to version control
- Store tokens securely using environment variables or secure secret management systems
- Rotate API tokens regularly and immediately if compromised
- Use the principle of least privilege when assigning API token permissions

### Data Handling
- All sensitive data should be encrypted in transit using HTTPS
- Avoid logging sensitive information from API responses
- Implement proper error handling to prevent data leaks in error messages
- Validate and sanitize all input data before sending to the Fibery API

### Dependencies
- Regular monitoring of dependencies for security vulnerabilities
- Automated security updates for dependencies through dependabot
- Enforced version constraints for all dependencies
- Regular security audits of the dependency tree

## Reporting a Vulnerability

We take security vulnerabilities seriously. Please report them following these steps:

1. **DO NOT** open a public GitHub issue if the bug is a security vulnerability
2. Email security concerns directly to security@aithena.co.uk
3. Include in your report:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to expect
- Acknowledgment of your report within 48 hours
- Regular updates on the progress of fixing the vulnerability
- Credit for responsible disclosure (if desired)
- Notification when the vulnerability is fixed

## Best Practices for Users

1. **API Token Management**
   - Use environment variables:
     ```python
     import os
     from fibery import FiberyService
     
     service = FiberyService(
         token=os.environ.get('FIBERY_TOKEN'),
         account=os.environ.get('FIBERY_ACCOUNT')
     )
     ```
   - Never hardcode tokens in your application code
   - Use unique tokens for different environments (development, staging, production)

2. **Error Handling**
   - Implement proper error handling to catch and handle FiberyErrors
   - Avoid exposing sensitive information in error messages
   - Log errors appropriately without exposing sensitive data

3. **Rate Limiting**
   - Use the built-in rate limiting features when performing batch operations
   - Implement appropriate delays between requests using the `delay` parameter
   - Monitor API usage to stay within rate limits

4. **Input Validation**
   - Validate all input data before sending to the API
   - Use type hints and Pydantic models for data validation
   - Implement appropriate sanitization for rich text content

## Automated Security Checks

This project uses several automated security measures:

- GitHub Security Alerts for dependency vulnerabilities
- CodeQL analysis for code scanning
- Automated dependency updates through Dependabot
- Regular security audits of dependencies

## Security-Related Configuration

When deploying applications using fibery-client, ensure:

1. SSL/TLS is properly configured
2. API tokens have appropriate scope and permissions
3. Logging is configured to exclude sensitive data
4. Error handling is implemented to prevent information disclosure

## Contact

For security-related inquiries, contact:
- Email: security@aithena.co.uk
- GPG Key: [security-key.asc](https://example.com/security-key.asc)

## Attribution

We appreciate the security research community and will acknowledge security researchers who responsibly disclose vulnerabilities to us.
