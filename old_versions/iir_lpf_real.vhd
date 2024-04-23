library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity iir_lpf_real is
	generic (
    	DATA_WIDTH : natural := 32;
    	OUTPUT_WIDTH : natural := 64;
    	COEFF_WIDTH: natural := 32;
    	FRAC_WIDTH: natural := 30
	);
	port (
    	data_i_i   : in std_logic_vector(DATA_WIDTH-1 downto 0);
    	data_en_i  : in std_logic;
    	data_clk_i : in std_logic;
    	data_rst_i : in std_logic;
    	data_i_o   : out std_logic_vector(OUTPUT_WIDTH-1 downto 0);
    	data_en_o  : out std_logic;
    	data_clk_o : out std_logic;
    	data_rst_o : out std_logic;
    	a1     	: in signed(COEFF_WIDTH-1 downto 0);
    	a1_en  	: in std_logic;
    	a1_clk 	: in std_logic;
    	a1_rst 	: in std_logic;
    	a2     	: in signed(COEFF_WIDTH-1 downto 0);
    	a2_en  	: in std_logic;
    	a2_clk 	: in std_logic;
    	a2_rst 	: in std_logic;
    	b0     	: in signed(COEFF_WIDTH-1 downto 0);
    	b0_en  	: in std_logic;
    	b0_clk 	: in std_logic;
    	b0_rst 	: in std_logic;
    	b1     	: in signed(COEFF_WIDTH-1 downto 0);
    	b1_en  	: in std_logic;
    	b1_clk 	: in std_logic;
    	b1_rst 	: in std_logic;
    	b2     	: in signed(COEFF_WIDTH-1 downto 0);
    	b2_en  	: in std_logic;
    	b2_clk 	: in std_logic;
    	b2_rst 	: in std_logic;
    	test1  	: out std_logic_vector(OUTPUT_WIDTH-1 downto 0);
    	test1_en   : out std_logic;
    	test1_clk   : out std_logic;
    	test1_rst  : out std_logic;
    	test2  	: out std_logic_vector(OUTPUT_WIDTH-1 downto 0);
    	test2_en   : out std_logic;
    	test2_clk  : out std_logic;
    	test2_rst  : out std_logic
	);
end entity iir_lpf_real;

architecture bhv of iir_lpf_real is

	----- CONSTANTS -----
	constant MUL_WIDTH : integer := COEFF_WIDTH + DATA_WIDTH; -- 32 + 16 = 48
	constant MUL_A_WIDTH : integer := COEFF_WIDTH + MUL_WIDTH; -- 32 + 48 = 80
	constant ASHIFT_WIDTH: integer := MUL_WIDTH - FRAC_WIDTH; -- 48 - 30 = 18
    
	----- SATURATION -----
	
	----- SIGNALS -----
	signal x_0, x_1, x_2: signed(DATA_WIDTH - 1 downto 0);
	signal y_2: signed(MUL_WIDTH - 1 downto 0);
	signal b0_m, b1_m, b2_m: signed(MUL_WIDTH - 1 downto 0);
	signal a1_m, a2_m: signed(MUL_A_WIDTH - 1 downto 0);
	signal iir_input, y_1: signed(MUL_A_WIDTH - 1 downto 0) := (others => '0');
	signal fir_output: signed(MUL_WIDTH - 1 downto 0);
	signal output, shifted_output: signed(MUL_A_WIDTH - 1 downto 0);
	signal a2_i, a1_i: signed(COEFF_WIDTH - 1 downto 0) := (others => '0');
	signal b0_i, b1_i, b2_i: signed(COEFF_WIDTH - 1 downto 0) := (others => '0');
	
	-- Add the attribute declaration here
    attribute dont_touch : string;
    -- Apply the attribute to the signals
    attribute dont_touch of y_2 : signal is "true";
    attribute dont_touch of x_1 : signal is "true";
    attribute dont_touch of y_1 : signal is "true";
    attribute dont_touch of x_2 : signal is "true";
    attribute dont_touch of iir_input : signal is "true";
    attribute dont_touch of shifted_output : signal is "true";
    attribute dont_touch of fir_output : signal is "true";

    
    
begin
	
    process(data_clk_i) is
	   begin
        if rising_edge(data_clk_i) then
           if data_rst_i = '1' then
                -- Reset internal states
                x_0 <= (others => '0');
                x_1 <= (others => '0');
                x_2 <= (others => '0');
                y_1 <= (others => '0');
                y_2 <= (others => '0');
                b0_m <= (others => '0');
                b1_m <= (others => '0');
                b2_m <= (others => '0');
                a1_m <= (others => '0');
                a2_m <= (others => '0');
                iir_input <= (others => '0');
                fir_output <= (others => '0');
                output <= (others => '0');
                a1_i <= (others => '0');
                a2_i <= (others => '0');
                b0_i <= (others => '0');
                b1_i <= (others => '0');
                b2_i <= (others => '0');
            else
        	-- Coefficients Load
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
       	 
        	-- Direct Form I
        	if data_en_i = '1' then
            	-- Update FIR values
            	x_2 <= signed(x_1); -- 32b
            	x_1 <= signed(x_0); -- 32b
            	x_0 <= signed(data_i_i); -- 32b
            	y_1 <= signed(shift_right(output,FRAC_WIDTH)); -- 64bit
                y_2 <= signed(y_1(MUL_WIDTH-1 downto 0));
                b0_m <= signed(x_0*b0_i); -- 32b * 32b (64b)
                b1_m <= signed(x_1*b1_i); -- 32b * 32b (64b)
                b2_m <= signed(x_2*b2_i); -- 32b * 32b (64b)
                a1_m <= signed(y_1(MUL_WIDTH-1 downto 0)*a1_i);
                a2_m <= signed(y_2*a2_i);
                --output <= b0_m + b1_m + b2_m - a1_m - a2_m;
                fir_output <= b0_m + b1_m + b2_m;
                iir_input <= resize(fir_output,MUL_A_WIDTH);
                output <= iir_input - a1_m - a2_m; 
                shifted_output <= shift_right(output, FRAC_WIDTH);

            	
            	--iir_input <= resize(fir_output,MUL_A_WIDTH);
            	--test1 <= std_logic_vector(iir_input(OUTPUT_WIDTH-1 downto 0));
            	
           	 end if;
           	 
        	end if;
    	end if;
	end process;

	data_i_o <= std_logic_vector(shifted_output(OUTPUT_WIDTH - 1 downto 0));
    	data_en_o <= data_en_i;
    	data_clk_o <= data_clk_i;
	data_rst_o <= data_rst_i;
	test1_en <= data_en_i;
	test1_clk <= data_clk_i;
	test1_rst <= data_rst_i;
	test2_en <= data_en_i;
	test2_clk <= data_clk_i;
	test2_rst <= data_rst_i;

end architecture bhv;
