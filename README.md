# generic similarity search
Fast multidimensional search for approximate nearest neighbours using FLANN (https://github.com/mariusmuja/flann).

[![Build Status](https://travis-ci.org/ImmobilienScout24/generic-similarity-search.svg?branch=master)](https://travis-ci.org/ImmobilienScout24/generic-similarity-search)

## API
To create your own similarity search you need to implement a generator based on the AbstractGenerator in the api package.

See the following basic example below:

    import os
    
    from generic_similarity_search.api.abstract_generator import AbstractGenerator
    from generic_similarity_search.api.row import Row
    
    
    class TestGenerator(AbstractGenerator):
        def needs_refresh(self):
            return True
    
        def parse_line(self, line: str):
            fields = line.strip().split(";")
    
            return Row(
                index_name=fields[3],
                fields={
                    "a": fields[0],
                    "b": fields[1],
                    "c": fields[2]
                })
    
        def get_index_config(self, index_name):
            config = {
                "index1": {
                    "a": {"weight": 1.0, "index": True},
                    "b": {"weight": 1.0, "index": True, "mapper": self.create_enum_mapper(["test1", "test2", "test3"])},
                    "c": {"weight": 1.0, "index": False}
                },
                "index2": {
                    "a": {"weight": 1.0, "index": True},
                    "b": {"weight": 1.0, "index": True, "mapper": self.create_enum_mapper(["test1", "test2", "test3"])},
                    "c": {"weight": 1.0, "index": False}
                }
            }
            return config[index_name]
    
        def get_data_url(self):
            return "file://" + os.path.join(os.path.join(os.path.dirname(__file__), "../../../unittest/resources/"), 'test.csv')

### Generator components

#### needs_refresh() [optional]
This method allows one to determine if data has changed and thus an index reload is required. It is called once per minute.
You don't need to implement it. The index gets rebuild when this function returns True.

#### parse_line(line: str)
This method contains your concrete implementation on how to parse a single line (the line string parameter) into the index fields.

#### get_index_config(index_name: str)
You need to implement this returning the configuration for your flann indices as a python dict containing the index names with fields and their configuration.
TODO: define config properties

#### get_data_url()
Return the url to load index data from. This can be an S3 url or a filesystem url.
Examples: 
    s3://my-bucket/my-key-prefix/ (loads all keys with the given prefix)
    s3://my-bucket/my-key-prefix/my-key
    file://my-folder/ (loads all files from folder)
    file://my-folder/my-file


## Configuration
    In case you want to deploy a web application alongside with your similarity search implementation,
    you ...

# Project setup
## use python 3.x
    pip install virtualenv
    virtualenv --python=python3 .venv
    source .venv/bin/activate

### install pybuilder
    pip install pybuilder

### install dependencies
    pyb install_dependencies

# Run tests
    pyb 

# Start example app
    ./scripts/run_test_generator.py
    curl http://localhost:8888/search?type=index1&a=1&b=test1&resultCount=2