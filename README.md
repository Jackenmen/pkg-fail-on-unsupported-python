# Package that can be conditionally depended on to get nice error messages about unsupported Python version

This package consist only of a source distribution (sdist) which, when built, will show an error about the lack of support for the current Python version.

The reason for this project's existence is mainly that upper-bound on `Requires-Python` is discouraged
due to a plethora of reasons, most of which are described in this blog post: \
https://iscinumpy.dev/post/bound-version-constraints/ \
With that said, for applications distributed through PyPI, it may make sense to still set an upper-bound on the project.

However:
- [`uv` ignores upper-bounds on `Requires-Python`](https://docs.astral.sh/uv/reference/internals/resolver/#requires-python)
- `pip`'s backtracking resolver will continue to try older versions of a package until it finds one that can be installed on current Python version **which will likely lead to the user installing an old version of the application**

Note that the problem of installing an older version of the application also exists when a lower-bound is specified on `Requires-Python` (and is common between `uv` and `pip`).

## How to use?

This package should be specified as a dependency and combined with the `python_version` environment marker as shown:
```
package-does-not-support-this-version-of-python; python_version >= '3.14'
```

This will prevent installation of the package on Python 3.14 and higher.

It is also possible to define a lower-bound:
```
package-does-not-support-this-version-of-python; python_version >= '3.14' or python_version < '3.8'
```
which can be useful to avoid backtracking to older version, when the user runs an older version of Python than supported.

---

**This package has two identical versions** - `1.0.1` is yanked and `1.0.0` isn't. This allows for some options in how the errors are presented.

---

For the upper-bound, it is recommended to only use the non-yanked version. The package will fail to install with a nice error:
```
$ pip install package-does-not-support-this-version-of-python
Processing package_does_not_support_this_version_of_python-1.0.0.tar.gz
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... error
  error: subprocess-exited-with-error

  × Preparing metadata (pyproject.toml) did not run successfully.
  │ exit code: 1
  ╰─> [4 lines of output]
      
      The project you're installing does not support the version of Python that you are currently using (3.14.1).
      For more details on supported Python version, read the documentation of the project that declares this package
      (package-does-not-support-this-version-of-python) in its dependencies.

      [end of output]
  
  note: This error originates from a subprocess, and is likely not a problem with pip.
error: metadata-generation-failed

× Encountered error while generating package metadata.
╰─> See above for output.

note: This is an issue with the package mentioned above, not pip.
hint: See above for details.
```
```
$ uv pip install package-does-not-support-this-version-of-python
Using Python 3.8.20 environment at: .venvs/3.8
Resolved 1 package in 1ms
  × Failed to build `package-does-not-support-this-version-of-python`
  ├─▶ The build backend returned an error
  ╰─▶ Call to `backend.build_wheel` failed (exit status: 1)

      [stderr]

      The project you're installing does not support the version of Python that you are currently using (3.14.1).
      For more details on supported Python version, read the documentation of the project that declares this package
      (package-does-not-support-this-version-of-python) in its dependencies.


      hint: This usually indicates a problem with the package or the build environment.
```

---

For the lower-bound, you can choose one of the 3 following options:
1.  Use the yanked version by pinning:
    ```
    package-does-not-support-this-version-of-python==1.0.1; python_version < '3.8'
    package-does-not-support-this-version-of-python; python_version >= '3.14'
    ```
    **When using a yanked version by pinning**, the users will see a warning when adding a package to a project whose `Requires-Python` is set below minimum supported version by your project:
    ```
    $ uv add your-cool-app
    Resolved 50 packages in 628ms
    warning: `package-does-not-support-this-version-of-python==1.0.1` is yanked (reason: "The project you're
     installing does not support the version of Python that you are currently using.")
    Prepared 10 packages in 248ms
    ░░░░░░░░░░░░░░░░░░░░ [0/45] Installing wheels...
    Installed 45 packages in 85ms
    [...]
    ```
    The package will fail to install with the nicer error shown earlier *but* that only works, if the user actually tests on their project's minimum supported version (which is, perhaps surprisingly, not always the case).
2.  Use the yanked version with a version range:
    ```
    package-does-not-support-this-version-of-python>=1.0.1,<=1.0.1; python_version < '3.8'
    package-does-not-support-this-version-of-python; python_version >= '3.14'
    ```
    **When using a yanked version with a version range**, the users will not be able to add the package to a project whose `Requires-Python` is set below minimum supported version by your project:
    ```
    $ uv add your-cool-app==1.2.3
      × No solution found when resolving dependencies for split (markers: python_full_version == '3.7.*'):
      ╰─▶ Because only package-does-not-support-this-version-of-python{python_full_version < '3.8'}<=1.0.1 is
            available and package-does-not-support-this-version-of-python{python_full_version < '3.8'}==1.0.1 was 
            yanked (reason: The project you're installing does not support the version of Python that you are
            currently using.), we can conclude that package-does-not-support-this-version-of-python{
            python_full_version < '3.8'}==1.0.1 cannot be used.
            And because your-cool-app==1.2.3 depends on package-does-not-support-this-version-of-python{
            python_full_version < '3.8'}==1.0.1, we can conclude that your-cool-app==1.2.3 cannot be used.
            And because only your-cool-app==1.2.3 is available and your project depends on your-cool-app, we can
            conclude that your project's requirements are unsatisfiable.
      help: If you want to add the package regardless of the failed resolution, provide the `--frozen` flag to skip
      locking and syncing.
    ```
    The downside of this approach is that the error will also look similarly unpleasant when installing the package:
    ```
    $ uv pip install your-cool-app==1.2.3
      × No solution found when resolving dependencies:
      ╰─▶ Because only package-does-not-support-this-version-of-python{python_full_version < '3.8'}<=1.0.1 is
            available and package-does-not-support-this-version-of-python{python_full_version < '3.8'}==1.0.1 was
            yanked (reason: The project you're installing does not support the version of Python that you are
            currently using.), we can conclude that package-does-not-support-this-version-of-python{
            python_full_version < '3.8'}==1.0.1 cannot be used.
            And because your-cool-app==1.2.3 depends on package-does-not-support-this-version-of-python{
            python_full_version < '3.8'}==1.0.1, we can conclude that your-cool-app==1.2.3 cannot be used.
            And because only your-cool-app==1.2.3 is available and you require your-cool-app, we can conclude
            that your requirements are unsatisfiable.
    ```
    or, in case of `pip`, won't even show the yank reason:
    ```
    $ pip install your-cool-app==1.2.3
    Collecting your-cool-app
      Downloading your_cool_app-1.2.3-py3-none-any.whl (6.0 MB)
         ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 6.0/6.0 MB 20.5 MB/s eta 0:00:00
    ERROR: Could not find a version that satisfies the requirement package-does-not-support-this-version-of-python
     <=1.0.1,>=1.0.1; python_version < "3.8" (from your-cool-app) (from versions: 1.0.0, 1.0.1)
    ERROR: No matching distribution found for package-does-not-support-this-version-of-python<=1.0.1,>=1.0.1;
     python_version < "3.8"
    ```
3.  Use the non-yanked version:
    ```
    package-does-not-support-this-version-of-python; python_version >= '3.14' or python_version < '3.8'
    ```

    **When using a non-yanked version**, there will no warning shown at all and only the installation will fail (with the nicer error shown earlier).

## Additional notes

You're more than welcome to publish this exact package on PyPI under a different name, if you want to have a different error message presented to the user. In fact, this repository actually builds 2 packages with different error messages already because I wanted a less generic error message on another project.

## License

Distributed under the MIT License. See ``LICENSE`` for more information.

---

> Jakub Kuczys &nbsp;&middot;&nbsp;
> GitHub [@Jackenmen](https://github.com/Jackenmen)
