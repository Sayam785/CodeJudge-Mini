-- Seed data.  Problem IDs and test IDs are never hard-coded: identity values
-- are returned by Oracle and test cases find their parent by title.
INSERT INTO Problems (title, description, difficulty, input_format, output_format, sample_input, sample_output, time_limit)
VALUES ('Sum of Two Numbers', 'Read two integers and print their sum.', 'Easy', 'Two integers a and b.', 'Print a+b.', '2 3', '5', 2);
INSERT INTO Problems (title, description, difficulty, input_format, output_format, sample_input, sample_output, time_limit)
VALUES ('Find Maximum', 'Read two integers and print the larger value.', 'Easy', 'Two integers.', 'Print the larger integer.', '8 3', '8', 2);
INSERT INTO Problems (title, description, difficulty, input_format, output_format, sample_input, sample_output, time_limit)
VALUES ('Even or Odd', 'Check whether a number is even or odd.', 'Easy', 'One integer n.', 'Print EVEN or ODD.', '12', 'EVEN', 2);
INSERT INTO Problems (title, description, difficulty, input_format, output_format, sample_input, sample_output, time_limit)
VALUES ('Factorial', 'Calculate the factorial of n.', 'Easy', 'One non-negative integer n.', 'Print n factorial.', '5', '120', 2);
INSERT INTO Problems (title, description, difficulty, input_format, output_format, sample_input, sample_output, time_limit)
VALUES ('Prime Number', 'Check whether a number is prime.', 'Easy', 'One positive integer.', 'Print YES or NO.', '15', 'NO', 2);
INSERT INTO Problems (title, description, difficulty, input_format, output_format, sample_input, sample_output, time_limit)
VALUES ('Sum of N Numbers', 'Calculate the sum of N numbers.', 'Easy', 'Read n followed by n integers.', 'Print the sum.', '4 1 2 3 4', '10', 2);
INSERT INTO Problems (title, description, difficulty, input_format, output_format, sample_input, sample_output, time_limit)
VALUES ('Reverse Number', 'Read a number and print its reverse.', 'Easy', 'One non-negative integer.', 'Print the reversed digits.', '12345', '54321', 2);
INSERT INTO Problems (title, description, difficulty, input_format, output_format, sample_input, sample_output, time_limit)
VALUES ('Palindrome Number', 'Check whether a number is a palindrome.', 'Easy', 'One non-negative integer.', 'Print YES or NO.', '1221', 'YES', 2);
INSERT INTO Problems (title, description, difficulty, input_format, output_format, sample_input, sample_output, time_limit)
VALUES ('Fibonacci Series', 'Print the first n Fibonacci numbers.', 'Easy', 'One integer n.', 'Print the series separated by spaces.', '5', '0 1 1 2 3', 2);
INSERT INTO Problems (title, description, difficulty, input_format, output_format, sample_input, sample_output, time_limit)
VALUES ('Count Digits', 'Count the number of digits in an integer.', 'Easy', 'One integer.', 'Print the number of decimal digits.', '987654', '6', 2);

INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '2 3', '5' FROM Problems WHERE title = 'Sum of Two Numbers';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '-7 10', '3' FROM Problems WHERE title = 'Sum of Two Numbers';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '0 0', '0' FROM Problems WHERE title = 'Sum of Two Numbers';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '8 3', '8' FROM Problems WHERE title = 'Find Maximum';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '-4 -9', '-4' FROM Problems WHERE title = 'Find Maximum';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '6 6', '6' FROM Problems WHERE title = 'Find Maximum';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '12', 'EVEN' FROM Problems WHERE title = 'Even or Odd';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '7', 'ODD' FROM Problems WHERE title = 'Even or Odd';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '0', 'EVEN' FROM Problems WHERE title = 'Even or Odd';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '0', '1' FROM Problems WHERE title = 'Factorial';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '5', '120' FROM Problems WHERE title = 'Factorial';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '7', '5040' FROM Problems WHERE title = 'Factorial';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '2', 'YES' FROM Problems WHERE title = 'Prime Number';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '15', 'NO' FROM Problems WHERE title = 'Prime Number';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '97', 'YES' FROM Problems WHERE title = 'Prime Number';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '4 1 2 3 4', '10' FROM Problems WHERE title = 'Sum of N Numbers';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '3 -5 0 2', '-3' FROM Problems WHERE title = 'Sum of N Numbers';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '1 42', '42' FROM Problems WHERE title = 'Sum of N Numbers';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '12345', '54321' FROM Problems WHERE title = 'Reverse Number';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '1200', '21' FROM Problems WHERE title = 'Reverse Number';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '7', '7' FROM Problems WHERE title = 'Reverse Number';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '1221', 'YES' FROM Problems WHERE title = 'Palindrome Number';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '1234', 'NO' FROM Problems WHERE title = 'Palindrome Number';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '0', 'YES' FROM Problems WHERE title = 'Palindrome Number';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '1', '0' FROM Problems WHERE title = 'Fibonacci Series';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '5', '0 1 1 2 3' FROM Problems WHERE title = 'Fibonacci Series';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '8', '0 1 1 2 3 5 8 13' FROM Problems WHERE title = 'Fibonacci Series';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '0', '1' FROM Problems WHERE title = 'Count Digits';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '987654', '6' FROM Problems WHERE title = 'Count Digits';
INSERT INTO TestCases (problem_id, input_data, expected_output) SELECT problem_id, '-42', '2' FROM Problems WHERE title = 'Count Digits';
COMMIT;
