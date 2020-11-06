import boto3

ssm = boto3.client("ssm", region_name="us-east-1")

variables = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_PASSWORD", "DEV", "DB_USER")

with open("/home/ec2-user/.env", "w") as env_file:
    for var in variables:
        parameter = (
            ssm.get_parameter(Name=var)["Parameter"]["Value"]
            .strip('"')
            .strip("'")
        )
        env_file.write(f"{var}={parameter}\n")
