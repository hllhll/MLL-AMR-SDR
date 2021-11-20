#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: hillel.ch
# GNU Radio version: v3.8.2.0-57-gd71cd177

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import analog
import math
from gnuradio import blocks
from gnuradio import digital
from gnuradio import filter
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio.qtgui import Range, RangeWidget
import epy_block_0
import epy_block_2_1
import osmosdr
import time

from gnuradio import qtgui

class record_decode_433(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "record_decode_433")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.sym_rate = sym_rate = 6000
        self.samp_rate_cap = samp_rate_cap = 0.250e6
        self.offset_tune = offset_tune = 10e3
        self.decoding_samp_per_sym = decoding_samp_per_sym = 8
        self.center_freq = center_freq = 465625000
        self.minimal_amplitude = minimal_amplitude = 0.001300
        self.fsk_deviation_hz = fsk_deviation_hz = 600
        self.decoding_samp_rate = decoding_samp_rate = (sym_rate*decoding_samp_per_sym)
        self.constellation_4fsk = constellation_4fsk = digital.constellation_calcdist([-1.5,-0.5,0.5,1.5], [0, 2, 4, 6],
        2, 1).base()
        self.constellation_4fsk.gen_soft_dec_lut(2)
        self.center_tune_freq = center_tune_freq = center_freq-offset_tune
        self.cap_sps = cap_sps = int(samp_rate_cap/sym_rate)
        self.available_bw = available_bw = samp_rate_cap-offset_tune*2
        self.acquire = acquire = 18*decoding_samp_per_sym

        ##################################################
        # Blocks
        ##################################################
        self._minimal_amplitude_range = Range(0, 0.1, 0.00001, 0.001300, 200)
        self._minimal_amplitude_win = RangeWidget(self._minimal_amplitude_range, self.set_minimal_amplitude, 'minimal_amplitude', "counter_slider", float)
        self.top_grid_layout.addWidget(self._minimal_amplitude_win)
        self.rtlsdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + "rtl_tcp=10.100.102.1"
        )
        self.rtlsdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.rtlsdr_source_0.set_sample_rate(samp_rate_cap)
        self.rtlsdr_source_0.set_center_freq(center_tune_freq, 0)
        self.rtlsdr_source_0.set_freq_corr(0, 0)
        self.rtlsdr_source_0.set_dc_offset_mode(0, 0)
        self.rtlsdr_source_0.set_iq_balance_mode(0, 0)
        self.rtlsdr_source_0.set_gain_mode(False, 0)
        self.rtlsdr_source_0.set_gain(38, 0)
        self.rtlsdr_source_0.set_if_gain(8, 0)
        self.rtlsdr_source_0.set_bb_gain(9, 0)
        self.rtlsdr_source_0.set_antenna('', 0)
        self.rtlsdr_source_0.set_bandwidth(0, 0)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=decoding_samp_rate,
                decimation=int(samp_rate_cap),
                taps=None,
                fractional_bw=0.0001)
        self.qtgui_time_sink_x_2 = qtgui.time_sink_f(
            8000*4, #size
            decoding_samp_rate, #samp_rate
            "", #name
            3 #number of inputs
        )
        self.qtgui_time_sink_x_2.set_update_time(0.10)
        self.qtgui_time_sink_x_2.set_y_axis(-0.04, 0.04)

        self.qtgui_time_sink_x_2.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_2.enable_tags(True)
        self.qtgui_time_sink_x_2.set_trigger_mode(qtgui.TRIG_MODE_AUTO, qtgui.TRIG_SLOPE_POS, 0.0, 0, 2, "")
        self.qtgui_time_sink_x_2.enable_autoscale(False)
        self.qtgui_time_sink_x_2.enable_grid(False)
        self.qtgui_time_sink_x_2.enable_axis_labels(True)
        self.qtgui_time_sink_x_2.enable_control_panel(False)
        self.qtgui_time_sink_x_2.enable_stem_plot(False)


        labels = ['avg', 'threshold', 'binary_threshold', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [2, 5, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(3):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_2.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_2.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_2.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_2.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_2.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_2.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_2.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_2_win = sip.wrapinstance(self.qtgui_time_sink_x_2.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_2_win)
        self.qtgui_time_sink_x_1_0 = qtgui.time_sink_f(
            decoding_samp_per_sym*180, #size
            decoding_samp_rate, #samp_rate
            "", #name
            1 #number of inputs
        )
        self.qtgui_time_sink_x_1_0.set_update_time(0.10)
        self.qtgui_time_sink_x_1_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_1_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_1_0.enable_tags(True)
        self.qtgui_time_sink_x_1_0.set_trigger_mode(qtgui.TRIG_MODE_TAG, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "squelch_sob")
        self.qtgui_time_sink_x_1_0.enable_autoscale(False)
        self.qtgui_time_sink_x_1_0.enable_grid(False)
        self.qtgui_time_sink_x_1_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_1_0.enable_control_panel(False)
        self.qtgui_time_sink_x_1_0.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_1_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_1_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_1_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_1_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_1_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_1_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_1_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_1_0_win = sip.wrapinstance(self.qtgui_time_sink_x_1_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_1_0_win)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            5000, #size
            decoding_samp_rate, #samp_rate
            "", #name
            2 #number of inputs
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-10, 10)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_TAG, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "squelch_sob")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['raw_signal', 'dc_offset_magic', 'filtered', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate_cap,
                6000,
                3500,
                firdes.WIN_HAMMING,
                6.76))
        self.epy_block_2_1 = epy_block_2_1.blk(tag_nameT="squelch_sob", tag_nameF="squelch_eob")
        self.epy_block_0 = epy_block_0.blk(reset_tag="squelch_sob", reset_tag_value="", lock_time=20*decoding_samp_per_sym, end_tag="'squelch_eob")
        self.digital_symbol_sync_xx_1 = digital.symbol_sync_ff(
            digital.TED_EARLY_LATE,
            decoding_samp_per_sym,
            0.48782,
            1,
            1.5,
            1.2,
            1,
            constellation_4fsk,
            digital.IR_MMSE_8TAP,
            128,
            [128])
        self.digital_constellation_decoder_cb_0 = digital.constellation_decoder_cb(constellation_4fsk)
        self.dc_blocker_xx_0_0 = filter.dc_blocker_ff(acquire, True)
        self.blocks_threshold_ff_0 = blocks.threshold_ff(0.000000000001, 0.000000000001, 0)
        self.blocks_tcp_server_sink_0 = blocks.tcp_server_sink(gr.sizeof_char*1, '0.0.0.0', 55525, False)
        self.blocks_tagged_file_sink_0 = blocks.tagged_file_sink(gr.sizeof_gr_complex*1, decoding_samp_rate)
        self.blocks_sub_xx_0 = blocks.sub_ff(1)
        self.blocks_repeat_0_0 = blocks.repeat(gr.sizeof_float*1, decoding_samp_per_sym)
        self.blocks_multiply_xx_1 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_ff(0.5)
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_ff(2)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(10000000)
        self.blocks_moving_average_xx_0 = blocks.moving_average_ff(decoding_samp_per_sym*10, 1, 4000, 1)
        self.blocks_float_to_complex_1 = blocks.float_to_complex(1)
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_float_to_char_1 = blocks.float_to_char(1, 1)
        self.blocks_delay_0_0 = blocks.delay(gr.sizeof_float*1, (acquire-1)*2)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(1)
        self.blocks_char_to_float_0 = blocks.char_to_float(1, 1)
        self.blocks_add_const_vxx_1 = blocks.add_const_ff(-minimal_amplitude)
        self.blocks_add_const_vxx_0 = blocks.add_const_ff(-3)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate_cap, analog.GR_COS_WAVE, -offset_tune, 1, 0, 0)
        self.analog_quadrature_demod_cf_0_0_0_1_0 = analog.quadrature_demod_cf(decoding_samp_rate/(2*math.pi*fsk_deviation_hz))
        self.analog_pwr_squelch_xx_1 = analog.pwr_squelch_cc(-400, 1, 0, True)
        self.analog_const_source_x_0 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, minimal_amplitude)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_const_source_x_0, 0), (self.qtgui_time_sink_x_2, 1))
        self.connect((self.analog_pwr_squelch_xx_1, 0), (self.epy_block_2_1, 0))
        self.connect((self.analog_quadrature_demod_cf_0_0_0_1_0, 0), (self.blocks_delay_0_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0_0_0_1_0, 0), (self.dc_blocker_xx_0_0, 0))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_add_const_vxx_0, 0), (self.blocks_float_to_char_1, 0))
        self.connect((self.blocks_add_const_vxx_0, 0), (self.blocks_repeat_0_0, 0))
        self.connect((self.blocks_add_const_vxx_1, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_char_to_float_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_moving_average_xx_0, 0))
        self.connect((self.blocks_delay_0_0, 0), (self.blocks_sub_xx_0, 0))
        self.connect((self.blocks_delay_0_0, 0), (self.epy_block_0, 0))
        self.connect((self.blocks_delay_0_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_float_to_char_1, 0), (self.blocks_tcp_server_sink_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.digital_constellation_decoder_cb_0, 0))
        self.connect((self.blocks_float_to_complex_1, 0), (self.blocks_multiply_xx_1, 1))
        self.connect((self.blocks_moving_average_xx_0, 0), (self.blocks_add_const_vxx_1, 0))
        self.connect((self.blocks_moving_average_xx_0, 0), (self.qtgui_time_sink_x_2, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_threshold_ff_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.blocks_add_const_vxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.digital_symbol_sync_xx_1, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.blocks_multiply_xx_1, 0), (self.analog_pwr_squelch_xx_1, 0))
        self.connect((self.blocks_repeat_0_0, 0), (self.qtgui_time_sink_x_1_0, 0))
        self.connect((self.blocks_sub_xx_0, 0), (self.epy_block_0, 1))
        self.connect((self.blocks_threshold_ff_0, 0), (self.blocks_float_to_complex_1, 0))
        self.connect((self.blocks_threshold_ff_0, 0), (self.qtgui_time_sink_x_2, 2))
        self.connect((self.dc_blocker_xx_0_0, 0), (self.blocks_sub_xx_0, 1))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.blocks_char_to_float_0, 0))
        self.connect((self.digital_symbol_sync_xx_1, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.epy_block_0, 0), (self.blocks_multiply_const_vxx_1, 0))
        self.connect((self.epy_block_0, 0), (self.qtgui_time_sink_x_0, 1))
        self.connect((self.epy_block_2_1, 0), (self.analog_quadrature_demod_cf_0_0_0_1_0, 0))
        self.connect((self.epy_block_2_1, 0), (self.blocks_tagged_file_sink_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_multiply_xx_1, 0))
        self.connect((self.rtlsdr_source_0, 0), (self.blocks_multiply_xx_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "record_decode_433")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_sym_rate(self):
        return self.sym_rate

    def set_sym_rate(self, sym_rate):
        self.sym_rate = sym_rate
        self.set_cap_sps(int(self.samp_rate_cap/self.sym_rate))
        self.set_decoding_samp_rate((self.sym_rate*self.decoding_samp_per_sym))

    def get_samp_rate_cap(self):
        return self.samp_rate_cap

    def set_samp_rate_cap(self, samp_rate_cap):
        self.samp_rate_cap = samp_rate_cap
        self.set_available_bw(self.samp_rate_cap-self.offset_tune*2)
        self.set_cap_sps(int(self.samp_rate_cap/self.sym_rate))
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate_cap)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate_cap, 6000, 3500, firdes.WIN_HAMMING, 6.76))
        self.rtlsdr_source_0.set_sample_rate(self.samp_rate_cap)

    def get_offset_tune(self):
        return self.offset_tune

    def set_offset_tune(self, offset_tune):
        self.offset_tune = offset_tune
        self.set_available_bw(self.samp_rate_cap-self.offset_tune*2)
        self.set_center_tune_freq(self.center_freq-self.offset_tune)
        self.analog_sig_source_x_0.set_frequency(-self.offset_tune)

    def get_decoding_samp_per_sym(self):
        return self.decoding_samp_per_sym

    def set_decoding_samp_per_sym(self, decoding_samp_per_sym):
        self.decoding_samp_per_sym = decoding_samp_per_sym
        self.set_acquire(18*self.decoding_samp_per_sym)
        self.set_decoding_samp_rate((self.sym_rate*self.decoding_samp_per_sym))
        self.blocks_moving_average_xx_0.set_length_and_scale(self.decoding_samp_per_sym*10, 1)
        self.blocks_repeat_0_0.set_interpolation(self.decoding_samp_per_sym)

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.set_center_tune_freq(self.center_freq-self.offset_tune)

    def get_minimal_amplitude(self):
        return self.minimal_amplitude

    def set_minimal_amplitude(self, minimal_amplitude):
        self.minimal_amplitude = minimal_amplitude
        self.analog_const_source_x_0.set_offset(self.minimal_amplitude)
        self.blocks_add_const_vxx_1.set_k(-self.minimal_amplitude)

    def get_fsk_deviation_hz(self):
        return self.fsk_deviation_hz

    def set_fsk_deviation_hz(self, fsk_deviation_hz):
        self.fsk_deviation_hz = fsk_deviation_hz
        self.analog_quadrature_demod_cf_0_0_0_1_0.set_gain(self.decoding_samp_rate/(2*math.pi*self.fsk_deviation_hz))

    def get_decoding_samp_rate(self):
        return self.decoding_samp_rate

    def set_decoding_samp_rate(self, decoding_samp_rate):
        self.decoding_samp_rate = decoding_samp_rate
        self.analog_quadrature_demod_cf_0_0_0_1_0.set_gain(self.decoding_samp_rate/(2*math.pi*self.fsk_deviation_hz))
        self.qtgui_time_sink_x_0.set_samp_rate(self.decoding_samp_rate)
        self.qtgui_time_sink_x_1_0.set_samp_rate(self.decoding_samp_rate)
        self.qtgui_time_sink_x_2.set_samp_rate(self.decoding_samp_rate)

    def get_constellation_4fsk(self):
        return self.constellation_4fsk

    def set_constellation_4fsk(self, constellation_4fsk):
        self.constellation_4fsk = constellation_4fsk

    def get_center_tune_freq(self):
        return self.center_tune_freq

    def set_center_tune_freq(self, center_tune_freq):
        self.center_tune_freq = center_tune_freq
        self.rtlsdr_source_0.set_center_freq(self.center_tune_freq, 0)

    def get_cap_sps(self):
        return self.cap_sps

    def set_cap_sps(self, cap_sps):
        self.cap_sps = cap_sps

    def get_available_bw(self):
        return self.available_bw

    def set_available_bw(self, available_bw):
        self.available_bw = available_bw

    def get_acquire(self):
        return self.acquire

    def set_acquire(self, acquire):
        self.acquire = acquire
        self.blocks_delay_0_0.set_dly((self.acquire-1)*2)





def main(top_block_cls=record_decode_433, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()

    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()

if __name__ == '__main__':
    main()
