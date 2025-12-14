# QTool - Couchbase Query CLI

A lightweight command-line tool for executing N1QL queries against Couchbase clusters with configuration management and formatted output.

## Features

- 🔐 Secure configuration storage for connection parameters
- 📊 Tabular display of query results in CSV format
- ⚡ Connection timeout management
- 🔄 Support for nested result flattening
- 📝 Query execution metrics (execution time)
- 🎨 Color-coded terminal output

## Installation

### Prerequisites
- Python 3.7+
- Couchbase Python SDK 3.x

### Install Dependencies
```bash
pip install couchbase click tabulate
```

### Clone and Setup
```bash
# Clone the repository or copy the script
git clone <repository-url>
cd qtool

# Make the script executable (optional)
chmod +x qtool.py

# Or install as a Python package
pip install -e .
```

## Quick Start

### 1. Configure Connection
First, set up your Couchbase cluster connection:

```bash
# Interactive mode (will prompt for each parameter)
python qtool.py configure

# Or provide parameters directly
python qtool.py configure \
  --address 192.168.1.100:8091 \
  --username Administrator \
  --password your_password
```

### 2. Execute Queries
Run N1QL queries against your configured cluster:

```bash
# Simple query
python qtool.py execute --query "SELECT * FROM `travel-sample` LIMIT 5"

# Query with alias
python qtool.py execute -q "SELECT COUNT(*) as total FROM `travel-sample`"

# Use different credentials for a specific query
python qtool.py execute \
  --address 10.0.0.50:8091 \
  --username admin \
  --password secret \
  --query "SELECT meta().id FROM `bucket-name` WHERE type = 'user'"
```

## Command Reference

### `configure`
Store connection parameters for future use.

**Options:**
- `-a, --address`: Cluster address (default: 127.0.0.1:8091)
- `-u, --username`: Username (default: Administrator)
- `-p, --password`: Password (will be hidden during input)

**Examples:**
```bash
# Minimal configuration (prompts for missing values)
python qtool.py configure

# Full configuration
python qtool.py configure --address cb.example.com:8091 --username dbadmin
```

### `execute`
Execute a N1QL query and display results.

**Options:**
- `-a, --address`: Override configured cluster address
- `-u, --username`: Override configured username
- `-p, --password`: Override configured password (will be hidden)
- `-q, --query`: N1QL query to execute (required)

**Examples:**
```bash
# Use stored configuration
python qtool.py execute --query "SELECT * FROM `sample-bucket` LIMIT 10"

# Override address for this query
python qtool.py execute --address cluster2:8091 -q "SELECT COUNT(*) FROM `users`"

# Complex query with JOIN
python qtool.py execute -q """
    SELECT u.name, o.total 
    FROM `users` u 
    JOIN `orders` o ON KEYS u.order_id 
    WHERE u.active = true
"""
```

## Configuration File

The tool stores configuration in `.configs.ini` in the same directory:

```ini
[CLUSTER]
address = 192.168.1.100:8091
username = Administrator
password = your_encrypted_password
```

**Note:** Passwords are stored in plain text. For production use, consider implementing encryption or using environment variables.

## Query Examples

### Basic Queries
```bash
# Count documents
python qtool.py execute -q "SELECT COUNT(*) as doc_count FROM `travel-sample`"

# Filter with WHERE
python qtool.py execute -q "SELECT * FROM `inventory` WHERE type = 'hotel' AND city = 'Paris'"

# Project specific fields
python qtool.py execute -q "SELECT name, email, country FROM `users` WHERE active = true"
```

### Advanced Queries
```bash
# Aggregation
python qtool.py execute -q """
    SELECT country, COUNT(*) as user_count, AVG(age) as avg_age
    FROM `users` 
    GROUP BY country 
    ORDER BY user_count DESC
"""

# Nested array querying
python qtool.py execute -q """
    SELECT name, 
           ARRAY hobby.name FOR hobby IN interests END as hobbies
    FROM `profiles`
    WHERE ANY hobby IN interests SATISFIES hobby.level = 'expert' END
"""

# Metadata queries
python qtool.py execute -q """
    SELECT META().id, META().cas, email, last_login
    FROM `session-store`
    WHERE expiration > NOW()
"""
```

### System Queries
```bash
# Check cluster health
python qtool.py execute -q "SELECT * FROM system:keyspaces"

# Monitor active requests
python qtool.py execute -q "SELECT * FROM system:active_requests"

# Get bucket information
python qtool.py execute -q "SELECT * FROM system:buckets"
```

## Output Format

The tool displays results in CSV format with:
- Index column showing row numbers
- Column headers from query results
- Flattened nested objects (e.g., `address.city` becomes `address.city`)
- Color-coded messages:
  - ✅ Green: Success messages
  - 📋 White: Query results
  - ⏱️ Yellow: Query execution time
  - ❌ Red: Error messages

**Example Output:**
```
CONNECTING TO '127.0.0.1:8091'
Executing query: SELECT * FROM `travel-sample` LIMIT 2

0,hotel_10025,{"address":"Capstone Road, ME7 3JE","alias":["Medway Youth Hostel"],...
1,hotel_10026,{"address":"Hilltop, Horton-cum-Studley, OX33 1BG","alias":null,...

Execution time: 45.2345ms
```

## Environment Variables (Alternative)

You can also use environment variables instead of configuration file:

```bash
export CB_ADDRESS=localhost:8091
export CB_USERNAME=Administrator
export CB_PASSWORD=password

python qtool.py execute -q "SELECT 1"
```

## Troubleshooting

### Common Issues

1. **Connection Failed**
   ```bash
   # Check if Couchbase is running
   curl http://localhost:8091/pools
   
   # Verify credentials
   python qtool.py configure --address localhost:8091 --username Administrator --password password
   ```

2. **SSL/TLS Issues**
   ```bash
   # For SSL connections, modify the connection string
   python qtool.py configure --address couchbases://your-cluster.com:11207
   ```

3. **Query Timeout**
   ```bash
   # The tool has a default 10-second query timeout
   # For longer queries, modify the timeout_options in the code
   ```

### Debug Mode
For detailed error information, you can modify the script to add debug logging or run with Python debug flags:

```bash
python -m pdb qtool.py execute -q "SELECT * FROM test"
```

## Security Considerations

1. **Password Storage**: Passwords are stored in plain text in `.configs.ini`
2. **Network Security**: Use TLS/SSL for production deployments
3. **File Permissions**: Ensure configuration file has proper permissions (`chmod 600 .configs.ini`)
4. **Connection Strings**: Use `couchbases://` for encrypted connections

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and feature requests, please:
1. Check the troubleshooting section
2. Review Couchbase documentation
3. Open an issue in the repository

---

**Happy Querying!** 🚀
