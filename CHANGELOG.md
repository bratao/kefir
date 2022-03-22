# v0.1.3
In developement
* Global restructuring to package.
* Add deserialization support.
* Big refactoring of `BaseKefir` class.
* Add `@dump_route` decorator, that dump view-func result. Flask and FastAPI support.
* Add (de)serealizing benchmarks.
* Enable CI tests.
# v0.1.2
20-09-2021
* New param `rels` needs for normal db relations support. Also Kefir checks classes where used `__slots__`.
# v0.1.1
12-08-2021
* Add support for nested data.
* Drop arg `one`, work on this later.
* Delete code for searching model id, be cause today kefir is need to full support db models. It was in 0.2.x release.
* Add Github Discussions for feedback.
* Fix potential bug, where regexp can catch classes created on same file, where dev uses kefir, but don't catch classes from other files.
* Rename function `dump_to_dict` to `dump` for better typing.
# v0.1.0
07-08-2021
Zero release.