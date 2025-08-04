import pytest                                                                   
import os                                                                       
import allure                                                                   
                                                                                
def pytest_addoption(parser):                                                   
    parser.addoption("--log-folder", action="store", required=True, help="Path to folder containing manual log files")
    parser.addoption("--supersuite", action="store", default="DefaultSuperSuite", help="Supersuite name")
    parser.addoption("--suite", action="store", default="DefaultSuite", help="Suite name")
                                                                                
def pytest_generate_tests(metafunc):                                            
    log_folder = metafunc.config.getoption("log-folder")                        
    log_files = [f for f in os.listdir(log_folder) if f.endswith(".txt")]          
    full_paths = [os.path.join(log_folder, f) for f in log_files]               
                                                                                
    if "log_file_path" in metafunc.fixturenames:                                
        metafunc.parametrize("log_file_path", full_paths)                       
                                                                                
@pytest.fixture(scope="session")                                                
def suite_metadata(request):                                                    
    return {                                                                    
        "supersuite": request.config.getoption("supersuite"),                   
        "suite": request.config.getoption("suite")                              
    }                                                                           
                                                                                
def test_manual_log(log_file_path, suite_metadata):                             
    test_case_name = os.path.splitext(os.path.basename(log_file_path))[0]          
                                                                                
    with open(log_file_path, "r", encoding="utf-8") as f:                       
        content = f.read()                                                      
                                                                                
    print(f"\n--- {test_case_name} ---\n{content}\n")                           
                                                                                
    # Add Allure metadata                                                       
    allure.dynamic.title(test_case_name)                                        
    allure.dynamic.suite(suite_metadata["suite"])                               
    allure.dynamic.parent_suite(suite_metadata["supersuite"])                   
    allure.attach(content, name="Manual Log", attachment_type=allure.attachment_type.TEXT)
                                                                                
    # Determine test status from log content                                    
    if "TEST PASSED" in content:                                                
        assert True, f"{test_case_name} passed"                                 
    elif "TEST FAILED" in content:                                              
        pytest.fail(f"{test_case_name} failed based on log content")            
    else:                                                                       
        pytest.skip(f"{test_case_name}: No pass/fail keyword found in log")
