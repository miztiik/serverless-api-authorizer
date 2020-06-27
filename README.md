# Serverless API Authorizer

Authentication is a tough problem almost. Doing it right is not easy. You need to balance usability and security. When you are building serverless application, like an API, you would want your APIs to be accessible by authenticated users.

If you want application A to talk to another application B then A needs to authenticate itself to B. A common use case for this is a script that talks to an API-Gateway or an application behind an Application Load balancer to get some data.

The appropriate authentication flow for `Machine-To-Machine` or `API-To-API` authentication is called `client credentials` and the process is fairly straightforward,

1. The machine (i.e. script/Lambda/Requestor) authenticates itself against a Cognito Endpoint with a list of desired scopes
1. Cognito verifies the credentials and checks if the machine is allowed to get these scopes
1. If the credentials are valid and the scopes can be granted, Cognito returns an Access Token to the machine
1. The machine can use that Access Token to Authenticate itself against the API-Gateway or an Application Load Balancer

`Scopes` are technically part of authorization. A scope more or less is a label that describes a capability such as **`VIEW_PROFILE`** or **`DELETE_MESSAGE`**. You can create as many scopes as you like, but without further processing they’re useless.

From the perspective of an _App_ you get information about which scopes the current user has been granted and you yourself are responsible for implementing authorization measures based on that. In this demo, we are going to see, How to securing your AWS API Gateway endpoints using Cognito User Pools.

![Miztiik Serverless API Authentication](images/miztiik-cloudwatch-embedded-metric-format-for-aws-lambda.png)

You can embed custom metrics alongside detailed log event data, and CloudWatch will automatically extract the custom metrics so you can visualize and alarm on them, for real-time incident detection.

Follow this article in **[Youtube](https://www.youtube.com/c/ValaxyTechnologies)**

1. ## 🧰 Prerequisites

    This demo, instructions, scripts and cloudformation template is designed to be run in `us-east-1`. With few modifications you can try it out in other regions as well(_Not covered here_).

    - 🛠 AWS CLI Installed & Configured - [Get help here](https://youtu.be/TPyyfmQte0U)
    - 🛠 AWS CDK Installed & Configured - [Get help here](https://www.youtube.com/watch?v=MKwxpszw0Rc)
    - 🛠 Python Packages, _Change the below commands to suit your OS, the following is written for amzn linux 2_
        - Python3 - `yum install -y python3`
        - Python Pip - `yum install -y python-pip`
        - Virtualenv - `pip3 install virtualenv`

1. ## ⚙️ Setting up the environment

    - Get the application code

        ```bash
        git clone https://github.com/miztiik/cloudwatch-embedded-metric.git
        cd cloudwatch-embedded-metric
        ```

1. ## 🚀 Resource Deployment using AWS CDK

    The cdk stack provided in the repo will create the following resources,
    - API GW to front end Application running inside Lambda

    ```bash
    # If you DONT have cdk installed
    npm install -g aws-cdk

    # Make sure you in root directory
    python3 -m venv .env
    source .env/bin/activate
    pip3 install -r requirements.txt
    ```

    The very first time you deploy an AWS CDK app into an environment _(account/region)_, you’ll need to install a `bootstrap stack`, Otherwise just go ahead and   deploy using `cdk deploy`.

    ```bash
    cdk bootstrap
    cdk deploy cloudwatch-embedded-metric
    # Follow on screen prompts
    ```

    `method.request.header.Authorization` should be the identity token source

1. ## 🔬 Testing the solution

    The _Outputs_ section of the Clouformation template/service has the required information.

    - Get the `ApiUrl`,
        - It should look like `https://877bvvfqnb.execute-api.us-east-1.amazonaws.com/myst/user_id/{likes}`
    - Instead of like `{likes}` use a number between `1 to 100`,
        - For example `https://877bvvfqnb.execute-api.us-east-1.amazonaws.com/myst/user_id/69`
        - Use this Url in the browser, you should see something similar,

        ```json
        {
        "message": {
            "_per_user_": "kon",
            "Environment": "production",
            "_aws": {
            "CloudWatchMetrics": [
                {
                "Namespace": "konstone-verse",
                "Dimensions": [
                    [
                    "_per_user_",
                    "Environment"
                    ]
                ],
                "Metrics": [
                    {
                    "Name": "likes_counter",
                    "Unit": "Count"
                    }
                ]
                }
            ],
            "Timestamp": 1587907680350
            },
            "likes_counter": 69
        }
        }
        ```

    - Navigate to `CloudWatch Metric` dashboard, you will find a new namespace `konstone-verse` along with a metric `likes_counter`

        You should be able to notice graphs similar to this,

        ![Miztiik Cloudwatch Embedded Metric for AWS Lambda](images/miztiik-cloudwatch-embedded-metric-format-for-aws-lambda-results.png)

1. ## 🧹 CleanUp

    If you want to destroy all the resources created by the stack, Execute the below command to delete the stack, or _you can delete the stack from console as well_

    - Resources created during [deployment](#-resource-deployment-using-aws-cdk)
    - Delete CloudWatch Lambda LogGroups
    - _Any other custom resources, you have created for this demo_

    ```bash
    # Delete from cdk
    cdk destroy

    # Delete the CF Stack, If you used cloudformation to deploy the stack.
    aws cloudformation delete-stack \
        --stack-name "MiztiikAutomationStack" \
        --region "${AWS_REGION}"
    ```

    This is not an exhaustive list, please carry out other necessary steps as maybe applicable to your needs.

## 📌 Who is using this

This repository to teaches cloudformation to new developers, Solution Architects & Ops Engineers in AWS. Based on that knowledge these Udemy [course #1][103], [course #2][102] helps you build complete architecture in AWS.

### 💡 Help/Suggestions or 🐛 Bugs

Thank you for your interest in contributing to our project. Whether it's a bug report, new feature, correction, or additional documentation or solutions, we greatly value feedback and contributions from our community. [Start here][200]

### 👋 Buy me a coffee

[![ko-fi](https://www.ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Q5Q41QDGK)Buy me a [coffee ☕][900].

### 📚 References

1. [Control access to a REST API using Amazon Cognito User Pools as authorizer][1]

1. [Authorize API access using custom scopes in Amazon Cognito][2]

1. [Allow users to invoke API Gateway REST API/Lambda using the execution role from an Amazon Cognito user pool group][3]

### 🏷️ Metadata

**Level**: 300

[1]: https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-integrate-with-cognito.html
[2]: https://aws.amazon.com/premiumsupport/knowledge-center/cognito-custom-scopes-api-gateway/
[3]: https://aws.amazon.com/premiumsupport/knowledge-center/cognito-user-pool-group/

[100]: https://www.udemy.com/course/aws-cloud-security/?referralCode=B7F1B6C78B45ADAF77A9

[101]: https://www.udemy.com/course/aws-cloud-security-proactive-way/?referralCode=71DC542AD4481309A441

[102]: https://www.udemy.com/course/aws-cloud-development-kit-from-beginner-to-professional/?referralCode=E15D7FB64E417C547579

[103]: https://www.udemy.com/course/aws-cloudformation-basics?referralCode=93AD3B1530BC871093D6

[200]: https://github.com/miztiik/cfn-challenges/issues

[899]: https://www.udemy.com/user/n-kumar/

[900]: https://ko-fi.com/miztiik
[901]: https://ko-fi.com/Q5Q41QDGK
