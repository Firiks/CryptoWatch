
# CryptoWatch

Cryptowatch is a serverless application that allows you to monitor the price of cryptocurrencies. You can set up alerts for when the price of a cryptocurrency increases or decreases by a certain percentage. To set up alert on specific cryptocurrencies, you must first add them to .env(create it from .env.example) file like `SYMBOLS="bitcoin,ethereum,..."`. The interval for checking the price of cryptocurrencies is in minutes and is set in the .env file as `EVENT_INTERVAL=5` and percentage treshold is set in `CHANGE=0.1`. The application is deployed on AWS using AWS CDK.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

## Diagram:
--------------------------

![Img](/img/diagram.png "Title")

## Prerequisites:
--------------------------
- Docker
- AWS Account
- AWS CLI

## Setup
--------------------------

Install AWS CDK

```
npm install -g aws-cdk
```

To manually create a virtualenv on MacOS and Linux:

```
$ python -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
$ .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code. This will take long time when running first time.

```
$ ./cdk-synth.sh {account_id} {region} {optional_cdk_args}
```

When running first time you must create bootstrap stack using:

```
$ cdk bootstrap
```

To deploy stack run:

```
$ ./cdk-deploy.sh {account_id} {region} {optional_cdk_args}
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk bootstrap`   deploys the CDK Toolkit staging stack, see [Bootstrapping](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html)
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
 * `cdk destroy`     destroy the stack(s)
