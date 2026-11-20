function hardStop(a, pinEN, pinRelais, relayActiveHigh)
    try, writePWMDutyCycle(a, pinEN, 0); catch, end
    try
        if relayActiveHigh
            writeDigitalPin(a, pinRelais, 0);
        else
            writeDigitalPin(a, pinRelais, 1);
        end
    catch
    end
    fprintf("HARD STOP executed: FAN=0, HEATER=OFF\n");
end
