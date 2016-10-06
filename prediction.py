#!/usr/bin/env python
"""
Print out the name of the best candidate based on historical data of
previous candidates.

The past candidates have a name, a list of tags and an interview count.
The new candidates have the same structure, but no interview count.
The interview count will be used to generate a score for each combination
of tags, which is then used to rank the new candidates, and the candidate with
the highest rank is output.

Running this script with `python prediction.py` will output the best choice.
Running this script with `python prediction.py -v` will output all existing
and new candidates ranked by score, and the best choice.


Since the candidates only have a name and tags, my first thought was to get an
average score for each individual tag based on the interview count, but several
of the past candidates were out of order when ranked by score.
Calculating an average score for each combination of tags based on the interview
count orders the past candidates very well, only two consecutive past
candidates are transposed.
"""

import json
import sys
from collections import defaultdict
from itertools import chain, combinations

def main(verbose):
    past_candidates = get_candidates_from_files([
        'past_candidates1.json',
        'past_candidates2.json',
        'past_candidates3.json'])

    scores = calculate_tag_combination_scores(past_candidates)

    if verbose:
        update_candidate_scores_and_sort(past_candidates, scores)
        print_candidates(past_candidates)

    # the README said the file would be named future_candidates.json,
    # but it appears to be named new_candidates.json
    new_candidates = get_candidates_from_files([
        'new_candidates.json'])

    update_candidate_scores_and_sort(new_candidates, scores)

    if verbose:
        print_candidates(new_candidates)

    the_winner = new_candidates[0].name

    print 'The candidate with the most interviews should be... ' + \
            the_winner + '\n'


class Candidate(object):
    '''
    Simple class to pull out some fields for easier access.
    '''
    def __init__(self, jsonobj):
        self.name = '{} {}'.format(jsonobj['User']['first_name'],
                                   jsonobj['User']['last_name'])
        self.tags = jsonobj['Tag']
        self.interview_count = int(jsonobj['User'].get('interview_count', 0))
        self.score = 0

    def __repr__(self):
        return '{:20} {:10}    {:5.2f}    {}'.format(
            self.name, self.interview_count, self.score,
            ', '.join(self.tags))

def get_candidates_from_files(filenames):
    '''
    Load json files and return a single list of candidates.
    '''
    candidates = []
    for filename in filenames:
        with open(filename) as fp:
            data = json.loads(fp.read())
            candidates += [Candidate(c) for c in data]
    return candidates

def print_candidates(candidates):
    print '{:20} {:10}    {:5}    {}'.format(
        'Name', 'Interviews', 'Score', 'Tags')
    print '-' * 79

    for candidate in candidates:
        print candidate

    print ''

def all_combinations(options):
    '''
    Return an iterable of all (ordered) combinations of the options.

    For example
    all_combinations([1, 2, 3]) returns:
        ((1,),     (2,),   (3,),
         (1, 2),   (1, 3), (2, 3),
         (1, 2, 3))
    '''
    return chain(
        *[combinations(options, x) for x in range(1, len(options)+1)]
    )

def calculate_tag_combination_scores(candidates):
    '''
    Calculates a score for each combination of a candidate's tags based on the
    average interview_count for the combination.

    Returns a dict of {tag combination: score}
    '''
    tag_combo_interview_counts = defaultdict(list)
    for candidate in candidates:
        for tag in all_combinations(candidate.tags):
            tag_combo_interview_counts[tag].append(candidate.interview_count)

    scores = {tag_combo: sum(counts) * 1.0 / len(counts)
              for tag_combo, counts in tag_combo_interview_counts.iteritems()}

    return scores

def update_candidate_scores_and_sort(candidates, scores):
    '''
    Updates each candidate's score attribute for each combination of
    the candidate's tags.

    Then sort the list of candidates in place,
    ordered by score and then interview count (largest first).
    '''
    for candidate in candidates:
        for tag in all_combinations(candidate.tags):
            candidate.score += scores.get(tag, 0)

    candidates.sort(
        key=lambda candidate: (candidate.score, candidate.interview_count),
        reverse=True)

if __name__ == '__main__':
    verbose_flag = sys.argv[-1] == '-v'
    main(verbose_flag)
