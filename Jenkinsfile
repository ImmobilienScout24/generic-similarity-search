pipeline {
	agent none

	options {
		disableConcurrentBuilds()
        skipStagesAfterUnstable()
        buildDiscarder(logRotator(numToKeepStr: '90', artifactNumToKeepStr: '90'))
        quietPeriod(30) // wait for 30 seconds to see if additional commits are coming in
	}

	environment {
        INVOKED_BUILD_NUMBER=getInvokedBuildNumber()
        FAST_TOKEN=getFastToken()
        FAST_USER=getFastUser()
        TWINE_USERNAME=getFastUser()
        TWINE_PASSWORD=getFastToken()
    }

    stages {
    	stage('Build, Test and Upload to Local PyPI') {
            agent { node { label 'deploy-python27' } }
            when {
                beforeAgent true
                branch 'master'
            }
            steps {
                sh 'pip install twine'
                sh 'pyb -C -E jenkins'
                sh 'twine upload --repository-url https://fast.cloud.scout24.com/artifactory/api/pypi/pypi-local target/dist/generic-similarity-search-1.0.dev0/dist/*'
            }
        }
    }
}