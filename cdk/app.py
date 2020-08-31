#!/usr/bin/env python3

from aws_cdk import core

from cdk.cdk_stack import CdkStack


app = core.App()
env_EU = core.Environment(account="709985471261", region="eu-west-1")
CdkStack(app, "windowspipeline", env=env_EU)

app.synth()
