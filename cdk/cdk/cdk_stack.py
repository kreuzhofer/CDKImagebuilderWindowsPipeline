from aws_cdk import (
    core,
    aws_imagebuilder as imagebuilder,
    aws_iam as iam,
    aws_ec2 as ec2
)


class CdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        cmp_chocoinstall = imagebuilder.CfnComponent(self, 
            "cmp_chocoinstall",
            name="InstallChocolatey",
            platform="Windows",
            version="1.0.0",
            uri="s3://imagebuildercustomcomponents/installchoco.yml"
            )        

        rcp = imagebuilder.CfnImageRecipe(self,
            "WindowsImageSampleRecipe",
            name="WindowsImageSampleRecipe",
            version="1.0.0",
            components=[
                {"componentArn":"arn:aws:imagebuilder:eu-west-1:aws:component/dotnet-core-runtime-windows/3.1.0/1"},
                {"componentArn":cmp_chocoinstall.attr_arn},
            ],
            parent_image="arn:aws:imagebuilder:eu-west-1:aws:image/windows-server-2019-english-core-base-x86/2020.8.12"
            )

        role = iam.Role(self, "WindowsImageSampleRole", role_name="WindowsImageSampleRole", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))
        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))
        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("EC2InstanceProfileForImageBuilder"))

        instanceprofile = iam.CfnInstanceProfile(self, 
            "WindowsImageSampleInstanceProfile",
            instance_profile_name="WindowsImageSampleInstanceProfile",
            roles=["WindowsImageSampleRole"]
        )

        vpc = ec2.Vpc.from_lookup(self, "VPC", vpc_name="default")
        subnet = vpc.public_subnets[0]
        print("Subnet Id: "+subnet.subnet_id)

        sg = ec2.SecurityGroup.from_security_group_id(self, "SG", security_group_id="sg-54f65620")
        print("Security Group: "+sg.security_group_id)
        
        infraconfig = imagebuilder.CfnInfrastructureConfiguration(self,
            "WindowsImageSampleInfrastructureConfig",
            name="WindowsImageSampleInfrastructureConfig",
            instance_types=["t3.xlarge"],
            instance_profile_name="WindowsImageSampleInstanceProfile",
            subnet_id=subnet.subnet_id,
            security_group_ids=[sg.security_group_id]
            )

        pipeline = imagebuilder.CfnImagePipeline(self,
            "WindowsImageSamplePipeline",
            name="WindowsImageSamplePipeline",
            image_recipe_arn=rcp.attr_arn,
            infrastructure_configuration_arn=infraconfig.attr_arn
            )