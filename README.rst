===============================
BitBucket Code Insight Reporter
===============================

Python module for creating Code Insight Reports based on llvm-based diagnostics output.

Installation
------------
.. code-block:: console

   $ pip install bitbucket-code-insight-reporter

Example
-------

Example LLVM output:

.. code-block:: console

    test.cpp:6:5: warning: use a trailing return type for this function [modernize-use-trailing-return-type]
    int main() {
    ~~~ ^
    auto       -> int
    test.cpp:11:9: warning: the 'empty' method should be used to check for emptiness instead of comparing to an empty object [readability-container-size-empty]
        if (hello + world == "")
            ^~~~~~~~~~~~~~~~~~~
            hello + world.empty()
    ../include/c++/v1/string:990:10: note: method 'basic_string'::empty() defined here
        bool empty() const _NOEXCEPT {return size() == 0;}
            ^
    test.cpp:11:29: warning: statement should be inside braces [readability-braces-around-statements]
        if (hello + world == "")
                                ^
                                {
    test.cpp:15:9: warning: use std::make_unique instead [modernize-make-unique]
        ptr.reset(new std::string{ "xyz" });
        ~^~~~~ ~~~~~~~~~~~~~~~~       ~
            = std::make_unique<std::string>
    test.cpp:16:15: warning: use nullptr [modernize-use-nullptr]
        ptr.reset(NULL);
                ^~~~
                nullptr
    test.cpp:19:5: warning: use range-based for loop instead [modernize-loop-convert]
        for (std::vector<int>::iterator it = vec.begin(); it != vec.end(); ++it)
        ^   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            (int & it : vec)
    test.cpp:19:10: warning: use auto when declaring iterators [modernize-use-auto]
        for (std::vector<int>::iterator it = vec.begin(); it != vec.end(); ++it)
            ^
    note: this fix will not be applied because it overlaps with another fix
    test.cpp:19:77: warning: statement should be inside braces [readability-braces-around-statements]
        for (std::vector<int>::iterator it = vec.begin(); it != vec.end(); ++it)
                                                                                ^
                                                                                {
                                                                                    
Example execution

.. code-block:: console

    code_insight_report_generator --id clang_format --title "Clang Format" --details "Overview of all warnings reported by Clang Format" --reporter "Bob Builder" --output ./path/to/report.json
    code_insight_reporter --bitbucket-server https://bitbucket.url.com --username bob --password builder --llvm-logging ./path/to/logging.out --bitbucket-project BOB --repository-slug builder --commit-hash 1234567890 --report-file ./path/to/report.json
    

Usage
-----

.. code-block:: console

    Usage: code_insight_report_generator [OPTIONS]

    Options:
    --id TEXT          Unique identifier for the report  [required]
    --title TEXT       Humand readable title for the Code Insight report
                        [required]

    --details TEXT     Additional details to share withing the Code Insight
                        report

    --reporter TEXT    Reference to the reporter of the Code Insight Report
    --link TEXT        Link towards an external report
    --logo-url TEXT    Link towards an image to be shown in the Code Insight
                        report

    --output FILENAME  Path towards the output file  [required]
    --help             Show this message and exit.

.. code-block:: console

    Usage: code_insight_reporter [OPTIONS]

    Options:
    --bitbucket-server TEXT   URL for the BitBucket server  [required]
    --username TEXT           Username associated with BitBucket  [required]
    --password TEXT           Password associated with BitBucket  [required]
    --llvm-logging TEXT       Path pointing to logging file containing llvm
                                diagnostics messages  [required]

    --bitbucket-project TEXT  BitBucket project name  [required]
    --repository-slug TEXT    BitBucket repository slug name  [required]
    --commit-hash TEXT        Commit Hash to associate the Code Insights Report
                                with  [required]

    --report-file FILENAME    Code Insights Report identifier  [required]
    --help                    Show this message and exit.
