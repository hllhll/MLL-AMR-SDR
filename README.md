# MLL-AMR-SDR
A Project for decoding Miltel (what I call) 2nd generation water AMR Transmitter/Reciver 4-FSK NBFM From air to usable data

Used in:
 * E-WEP/I-WEP 433 External transmitter
 * Dorot-valves MJ Residentual water meter (Embedded transmitter),
 * Others?

FCC: Somehow I was able to find **[this](https://fccid.io/ANATEL/01493-15-03592/Manual_E-WEP-433/7F933824-B3EF-489A-9741-D98BEC47BBA5/PDF)**, [2](https://fccid.io/ANATEL/01493-15-03592/), [3](https://israelpatents.justice.gov.il/en/patent-file/details/223224) after insane amount of online search
  Using this confirmed my observations and narrowed my baudrate down.

**How did I do it**
All information was recovered by open means, without access to firmware/opening device (somewhat illegal).
Mostly just analysis of transmittions and using a magnet to induce them.
More information to be provided.

**Tech spec:**
  * Frequency, In my area: 465.65 Mhz
  * Modulation: 4-Level FSK (4FSK)
  * Encoding: Texas Instruments / CC1120 - Data Whitning 
  * Frame: Variable length, No CC11xx "address field", With CRC16
  * Data: Encapsulated and hirachical Type, Len, Values (TLVs)
  * SYNC Word:
      * 32 bit Modulated as 2FSK (Seec CC1120 Datasheet, This is how it works)
      * Binary: 10010011000010110101000111011110; Hex(First bit recived MSB) 93 0b 51 de (0x930b51de)
      * Baseband: 1-High; 0-Low
      * This is the default SYNC word in TI documentation and code examples.
      * TI cc11xx SYMBOL_MAP_CFG = 00b
  * Preamble Modulated as 2FSK: 101010....10 <sync>

**Additional information:**
Device wakes up some time, when it wakes up it reports it's timestamp to it's basesstation.
Basesstation responds with an updated time.
When it wakes up, it might also deliver reading information in a couple of format (see protocol)
