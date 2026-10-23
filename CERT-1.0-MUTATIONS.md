# unidash 1.0.0 mutation rounds (item 18)

The mutation tables of the 1.0.0 certification; the summary is in CERT-1.0-REPORT.md.

## First author round

Each mutant applied alone to a copy of the tree at c76b0e7 (fetched Unicode data and the
oracle packages present), full suite with `-x` and bytecode off, on another machine with
CPython 3.14.2; the unmutated tree passed first. All 37 killed; the last column is the first
test that failed. M37 came with its test at 6101860 and was run alone on this PC.

| Mutant | Change | First failing test |
| --- | --- | --- |
| M01 | message quote limit ten times larger | `test_contract_api.py::test_messages_quote_at_most_forty_characters[41]` |
| M02 | off by one at the quote limit | `test_contract_api.py::test_a_forty_character_form_is_quoted_whole` |
| M03 | str subclass kept as given | `test_contract_api.py::test_str_subclasses_are_read_as_their_characters` |
| M04 | form compared through the subclass __eq__ | `test_contract_api.py::test_a_str_subclass_form_must_spell_a_form` |
| M05 | flags accept any truthy value | `test_contract_api.py::test_every_folder_checks_its_options_the_same_way[fold_dashes]` |
| M06 | wrong parameter name in the chunk error | `test_contract_api.py::test_a_bad_chunk_is_named_when_it_is_read` |
| M07 | three-em dash as wide as two-em in tex | `test_dashes.py::test_tex_widens_the_long_dashes` |
| M08 | script hyphen switch inverted | `test_cli.py::test_dash_options_reach_the_fold` |
| M09 | soft hyphen switch inverted | `_dashes.py::unidash._dashes.dash_table` |
| M10 | typographic script hyphens to ASCII | `test_cli.py::test_dash_options_reach_the_fold` |
| M11 | typographic drops the compatibility forms | `_dashes.py::unidash._dashes.fold_dashes` |
| M12 | swung dash to hyphen instead of tilde | `test_dashes.py::test_wavy_dashes_become_a_tilde` |
| M13 | Unicode 14 oblique hyphen dropped | `__init__.py::unidash` |
| M14 | vertical en dash target swapped with em | `test_dashes.py::test_typographic_unifies_the_compatibility_forms` |
| M15 | astral script hyphen dropped | `__init__.py::unidash` |
| M16 | subscript minus missing from the kept marks | `__init__.py::unidash` |
| M17 | leading BOM takes a column | `test_cli.py::test_a_bom_survives_filtering_and_takes_no_column` |
| M18 | CRLF counted as two line ends | `test_fuzz.py::test_find_dashes_positions_match_an_independent_count[11]` |
| M19 | columns counted from 0 | `__init__.py::unidash.DashHit` |
| M20 | code point not padded to four digits | `_dashes.py::unidash._dashes.find_dashes` |
| M21 | names taken from the interpreter only | `test_tools.py::test_find_names_do_not_depend_on_the_interpreter_tables` |
| M22 | a lone CR does not end a line | `test_fuzz.py::test_find_dashes_positions_match_an_independent_count[11]` |
| M23 | is_dash accepts the empty string | `test_contract_api.py::test_is_dash_errors` |
| M24 | streaming reads every chunk at once | `test_contract_api.py::test_a_bad_chunk_is_named_when_it_is_read` |
| M25 | dash_table hands out the shared cached table | `test_contract_api.py::test_dash_table_is_fresh_and_equals_what_fold_uses` |
| M26 | fullwidth offset off by one | `_fold.py::unidash._fold.to_ascii_punct` |
| M27 | fullwidth tilde (CP932 wave dash) dropped | `test_fold.py::test_fullwidth_punctuation_folds_to_its_nfkc_ascii_form` |
| M28 | ellipsis to two dots | `test_docs.py::test_each_example_prints_what_its_comments_say[3]` |
| M29 | a finding hides an earlier read error | `test_cli.py::test_errors_win_over_findings_in_check` |
| M30 | stdin may be named twice | `test_cli.py::test_stdin_twice_is_refused` |
| M31 | closed pipe reported as success | `test_cli.py::test_a_closed_pipe_stops_quietly` |
| M32 | --punct accepts --keep-soft-hyphens | `test_cli.py::test_punct_refuses_dash_options` |
| M33 | DashHit pickles through the private module | `test_contract_api.py::test_dash_hit_is_a_named_tuple_that_pickles_as_public` |
| M34 | to_ascii_punct takes any object | `test_contract_api.py::test_text_must_be_a_str[to_ascii_punct]` |
| M35 | wrong error type for a non-str | `test_contract_api.py::test_every_folder_checks_its_options_the_same_way[fold_dashes]` |
| M36 | filter rewrites CRLF line ends | `test_cli.py::test_stdin_is_filtered_to_stdout_byte_exactly` |
| M37 | `python -m unidash` guard removed | `test_cli.py::test_importing_the_main_module_does_not_run_the_tool` |

## Second author round

On the code the QA fixes of rounds 1 and 2 added: each mutant alone on `git archive d9dc54f` plus the
fetched data, CPython 3.13.2 with the oracles and mypy, full suite with `-x`, on this PC; the
unmutated tree passed first. All 15 killed.

| Mutant | Change | First failing test |
| --- | --- | --- |
| M38 | diagnostics printed with no stderr | `test_cli_io.py::test_with_no_stderr_diagnostics_stay_out_of_the_output[check0]` |
| M39 | usage error limit 100 times larger | `test_cli_io.py::test_a_huge_unknown_argument_is_cut_short[args0]` |
| M40 | long usage error kept whole | `test_cli_io.py::test_a_huge_unknown_argument_is_cut_short[args0]` |
| M41 | usage error printed with no stderr | `test_cli_io.py::test_with_no_stderr_a_usage_error_writes_nothing` |
| M42 | missing stdin not reported | `test_cli_edges.py::test_a_missing_stdin_is_reported_and_other_files_still_run` |
| M43 | missing stdout not reported | `test_cli_edges.py::test_a_missing_stdout_is_an_error[check0]` |
| M44 | Windows closed pipe (EINVAL) not recognised | `test_cli_edges.py::test_a_reader_that_leaves_early_stops_check_quietly` |
| M45 | every write error taken for a closed reader | `test_cli_io.py::test_a_write_error_other_than_a_closed_reader_is_raised` |
| M46 | stdout not silenced after the reader left | `test_cli_edges.py::test_a_reader_that_leaves_early_stops_check_quietly` |
| M47 | last character of each block dropped | `test_scale.py::test_a_long_text_folds_like_its_characters` |
| M48 | form names read case-insensitively | `test_cli_io.py::test_form_names_are_case_sensitive[ASCII]` |
| M49 | invalid form echoed whole | `test_cli_edges.py::test_a_huge_form_value_is_quoted_short` |
| M50 | BOM stripped from stdin | `test_cli_io.py::test_a_bom_on_stdin_is_kept[args0]` |
| M51 | non UTF-8 file accepted | `test_cli_io.py::test_a_file_that_is_not_utf8_is_an_error_and_others_still_run` |
| M52 | text of one block or less left unfolded | `__init__.py::unidash` |


## Third author round

On the code the QA round 3 fixes added: each mutant alone on `git archive 6b342cc` plus the
fetched data, CPython 3.13.2 with the oracles and mypy, full suite with `-x`, on this PC; the
unmutated tree passed first. All 14 killed. M63 and M64 are the two mutants QA lens e found
surviving at 6fa3a04.

| Mutant | Change | First failing test |
| --- | --- | --- |
| M53 | file name shortened at exactly 200 characters | `test_cli_names.py::test_file_names_are_shortened_only_past_two_hundred_characters[200-False]` |
| M54 | huge file name kept whole | `test_cli_names.py::test_a_huge_file_name_is_cut_short_in_the_error[check0]` |
| M55 | long file name loses its end | `test_cli_names.py::test_a_huge_file_name_is_cut_short_in_the_error[check0]` |
| M56 | read error repeats the file name | `test_cli_names.py::test_a_missing_file_is_reported_with_its_name_and_reason` |
| M57 | no fallback for lone surrogates in names | `test_cli_names.py::test_check_reports_a_name_with_a_lone_surrogate_escaped` |
| M58 | lone surrogates replaced by question marks | `test_cli_names.py::test_check_reports_a_name_with_a_lone_surrogate_escaped` |
| M59 | name refused by the system not caught | `test_cli_names.py::test_a_name_with_a_nul_is_reported_and_others_still_run[check0]` |
| M60 | --punct accepts an explicit --form ascii | `test_cli_names.py::test_punct_refuses_any_explicit_form[ascii]` |
| M61 | --form default restored to ascii | `test_cli.py::test_punct_folds_all_punctuation` |
| M62 | future import back on DashHit | `test_contract.py::test_dash_hit_fields_carry_their_real_types` |
| M63 | U+2028 ends a line (lens e N07) | `test_fuzz.py::test_find_dashes_positions_match_an_independent_count[11]` |
| M64 | usage error cut at exactly 200 (lens e N13) | `test_cli_io.py::test_usage_errors_are_cut_only_past_two_hundred_characters[200-False]` |
| M65 | usage error cut one character short | `test_cli_io.py::test_usage_errors_are_cut_only_past_two_hundred_characters[201-True]` |
| M66 | vertical tab and form feed end a line | `test_fuzz.py::test_find_dashes_positions_match_an_independent_count[11]` |
