LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.numeric_std.ALL;

entity iir_lpf_biquad_2c is
    generic (
        DATA_WIDTH : natural := 32;
        COEFF_WIDTH: natural := 32;
        OUTPUT_WIDTH : natural := 64;
        FRAC_WIDTH: natural := 30
    );
    port (
        data_i_i   : in std_logic_vector(DATA_WIDTH-1 downto 0);
        data_en_i  : in std_logic;
        data_clk_i : in std_logic;
        data_rst_i : in std_logic;
        ref_clk_i : in std_logic;
	   ref_rst_i : in std_logic;
        data_i_o   : out std_logic_vector(OUTPUT_WIDTH-1 downto 0);
        data_en_o  : out std_logic;
        data_clk_o : out std_logic;
        data_rst_o : out std_logic;
        a1         : in signed(COEFF_WIDTH-1 downto 0);
        a1_en      : in std_logic;
        a1_clk     : in std_logic;
        a1_rst     : in std_logic;
        a2         : in signed(COEFF_WIDTH-1 downto 0);
        a2_en      : in std_logic;
        a2_clk     : in std_logic;
        a2_rst     : in std_logic;
        b0         : in signed(COEFF_WIDTH-1 downto 0);
        b0_en      : in std_logic;
        b0_clk     : in std_logic;
        b0_rst     : in std_logic;
        b1         : in signed(COEFF_WIDTH-1 downto 0);
        b1_en      : in std_logic;
        b1_clk     : in std_logic;
        b1_rst     : in std_logic;
        b2         : in signed(COEFF_WIDTH-1 downto 0);
        b2_en      : in std_logic;
        b2_clk     : in std_logic;
        b2_rst     : in std_logic;
        test         : out std_logic_vector(1 downto 0);
        test_en      : out std_logic;
        test_clk     : out std_logic;
        test_rst     : out std_logic
    );
end iir_lpf_biquad_2c;

architecture bhv of iir_lpf_biquad_2c is
    type STATE_TYPE is (idle, truncate, sum1, done);
    signal state : STATE_TYPE;
    constant MUL_WIDTH : integer := COEFF_WIDTH + DATA_WIDTH;
    constant MUL_A_WIDTH : integer := COEFF_WIDTH + MUL_WIDTH;

    -- Input and coefficient signals
    signal nINP,nZX0, nZX1, nZX2: signed(DATA_WIDTH-1 downto 0) := (others => '0');
    signal nZY1, nZY2: signed(MUL_WIDTH-1 downto 0) := (others => '0');
    signal b0_i: signed(COEFF_WIDTH-1 downto 0) := (others => '0');
    signal b1_i: signed(COEFF_WIDTH-1 downto 0) := (others => '0');
    signal b2_i: signed(COEFF_WIDTH-1 downto 0) := (others => '0');
    signal a1_i: signed(COEFF_WIDTH-1 downto 0) := (others => '0');
    signal a2_i: signed(COEFF_WIDTH-1 downto 0) := (others => '0');

    -- Intermediate computation signals
    signal nGB0, nGB1, nGB2, nGA1, nGA2: signed(MUL_A_WIDTH-1 downto 0) := (others => '0');
    signal nSB0, nSB1, nSB2, nSA1, nSA2: signed(MUL_A_WIDTH-1 downto 0) := (others => '0');

    -- Final output signal
    signal nYOUT: std_logic_vector(MUL_A_WIDTH-1 downto 0) := (others => '0');
    
    attribute dont_touch : string;
    -- Apply the attribute to the signals
    attribute dont_touch of nZX0, nZX1, nZX2: signal is "true";
    attribute dont_touch of nZY1, nZY2 : signal is "true";
    attribute dont_touch of nGB0, nGB1, nGB2, nGA1, nGA2 : signal is "true";
    attribute dont_touch of nSB0, nSB1, nSB2, nSA1, nSA2 : signal is "true";

begin

    

    process(ref_clk_i,ref_rst_i)
    begin
        if rising_edge(ref_clk_i) then
            if a1_en = '1' then
                    a1_i <= a1;
                end if;
                if a2_en = '1' then
                    a2_i <= a2;
                end if;
                if b0_en = '1' then
                    b0_i <= b0;
                end if;
                if b1_en = '1' then
                    b1_i <= b1;
                end if;
                if b2_en = '1' then
                    b2_i <= b2;
                end if;
            if ref_rst_i = '0' then
                -- Reset logic
                state <= idle;
                nZX0 <= (others => '0');
                nZX1 <= (others => '0');
                nZX2 <= (others => '0');
                nGB0 <= (others => '0');
                nGB1 <= (others => '0');
                nGB2 <= (others => '0');
                nGA1 <= (others => '0');
                nGA2 <= (others => '0');
                nYOUT <= (others => '0');
                data_i_o <= (others => '0');
                a1_i <= (others => '0');
                a2_i <= (others => '0');
                b0_i <= (others => '0');
                b1_i <= (others => '0');
                b2_i <= (others => '0');  
                data_en_o <= '0';
                case state is
                    when idle =>
                        data_en_o <= '0'; -- Reset enable output
                        if data_en_i = '1' then
                            -- Load the input data
                            nINP <= signed(data_i_i);
                            nZX0 <= nINP; -- Load current input
                            nZX1 <= nZX0;              -- Shift previous inputs
                            nZX2 <= nZX1;
                            nGB0 <= resize(signed(b0_i) * nZX0,MUL_A_WIDTH); --32*32 = 64b
                            nGB1 <= resize(signed(b1_i) * nZX1,MUL_A_WIDTH); 
                            nGB2 <= resize(signed(b2_i) * nZX2,MUL_A_WIDTH);
                            nGA1 <= resize(signed(a1_i) * signed(nZY1),MUL_A_WIDTH); -- 32*64 = 96b
                            nGA2 <= resize(signed(a2_i) * signed(nZY2),MUL_A_WIDTH);
                            state <= truncate;
                            test <= "00";
                        end if;

                    when truncate =>

                        nSB0 <= shift_right(nGB0, FRAC_WIDTH);
                        nSB1 <= shift_right(nGB1, FRAC_WIDTH);
                        nSB2 <= shift_right(nGB2, FRAC_WIDTH);
                        nSA1 <= shift_right(nGA1, FRAC_WIDTH);
                        nSA2 <= shift_right(nGA2, FRAC_WIDTH);
                        state <= sum1;
                        test <= "01";

                    when sum1 =>
                        -- Sum up the products, accounting for feedback
                        nYOUT <= std_logic_vector(nSB0 + nSB1 + nSB2 - nSA1 - nSA2);
                        state <= done;
                        test <= "10";

                    when done =>
                        -- Assign the computed value to the output
                        data_i_o <= nYOUT(OUTPUT_WIDTH-1 downto 0);
                        nZY1     <= signed(nYOUT(OUTPUT_WIDTH-1 downto 0));
                        nZY2     <= nZY1;
                        data_en_o <= '1'; -- Signal that output is valid
                        state <= idle; -- Ready for the next input
                        test <= "11";

                    when others =>
                        state <= idle;
                end case;
            end if;
        end if;      
    end process;  
end architecture bhv;
