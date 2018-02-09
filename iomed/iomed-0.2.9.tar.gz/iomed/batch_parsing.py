import os
import json
import logging
import time


def parse_texts(all_texts, fname_out, pmel, block_size=100):

    start = time.time()

    if os.path.exists(fname_out):
        with open(fname_out) as fh:
            ready = json.load(fh)

    else:
        ready = []

    n_already_processed = len(ready)
    texts_processed = [r['text'] for r in ready]
    annots_processed = [r['annotations'] for r in ready]
    total_chars = sum(len(text) for text in all_texts)

    for i in range(n_already_processed, len(all_texts), block_size):
        begin_block = i
        end_block = i + block_size
        logging.info('Parsing block {} to {} of {}'.format(
            begin_block, end_block, len(all_texts)
        ))
        block_start = time.time()
        texts_to_process = all_texts[begin_block:end_block]
        annots = pmel.process(texts_to_process)

        texts_processed.extend(texts_to_process)
        annots_processed.extend(annots)

        with open(fname_out, 'w') as fh:
            json.dump([
                {
                    'text': text,
                    'annotations': annots
                } for text, annots in zip(texts_processed, annots_processed)
            ], fh)

        block_end = time.time()
        block_time = block_end - block_start
        time_so_far = block_end - start
        chars_so_far = sum(len(text) for text in texts_processed)
        time_per_char = time_so_far / chars_so_far
        expected_remaining_time = time_per_char * (total_chars - chars_so_far)
        logging.info('Block took {} seconds'.format(block_time))
        logging.info('Expected time to end: {:.2f} hours.'.format(
            expected_remaining_time / 3600))

    end = time.time()
    logging.info('Total time: {} seconds'.format(end - start))
