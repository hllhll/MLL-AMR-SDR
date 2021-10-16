"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr
import pmt

class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, reset_tag="", reset_tag_value="", lock_time=20, end_tag=""):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Tagged burst frequency lock',   # will show up in GRC
            in_sig=[np.float32, np.float32],
            out_sig=[np.float32]
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).

        self._reset_tag = reset_tag
        self._reset_tag_value = reset_tag_value
        self._lock_len = lock_time
        self._end_tag = end_tag
        self._reset()

    def get_tag_rel_offsets(self, data, inpnum, tagname):
    #def get_tags_rel_offsets(self, data, inpnum):
        ret = []
        tags = self.get_tags_in_window(inpnum, 0, len(data))
        for tag in tags:
            key = pmt.to_python(tag.key) # convert from PMT to python string
            value = pmt.to_python(tag.value) # Note that the type(value) can be several things, it depends what PMT type it was
            if key==tagname:
                item ={
                    'reloff': tag.offset - self.nitems_read(inpnum),
                    'name': tagname
                }
                ret.append(item)
        return ret

    def get_start_tag_rel_offsets(self, data, inpnum):
        return self.get_tag_rel_offsets( data, inpnum, self._reset_tag)

    def get_end_tag_rel_offsets(self, data, inpnum):
        return self.get_tag_rel_offsets( data, inpnum, self._end_tag)

    def _reset(self):
        self._state = 0
        self._lock_counter = 0
        self._lock_value = 0.0

    def work(self, input_items, output_items):
        signal = input_items[0]
        dc_off = input_items[1]
        # self.get_tags_in_window(which_input, rel_start, rel_end)
        # Will return a list of tags for the current window (input items)
        start_tag_poss = self.get_start_tag_rel_offsets(signal, 0)
        end_tag_poss = self.get_end_tag_rel_offsets(signal, 0)
        for i in range(len(signal)):
            for tag in start_tag_poss:
                if i==tag['reloff'] and tag['name']==self._reset_tag:
                    # Reset detected
                    self._reset()
                    break # Next i

            if self._state == 0: # Aquire
                self._lock_counter += 1
                if self._lock_counter == self._lock_len: # End aquire
                    self._state = 1;
                    self._lock_value = dc_off[i]
                    #print("lock " + str(self._lock_value))
                output_items[0][i] = signal[i] - dc_off[i] # Plain DC Block
            else:
                # Lock DC Value
                output_items[0][i] = signal[i] - self._lock_value
        return len(output_items[0])


