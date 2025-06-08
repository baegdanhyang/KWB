package com.application.KWB.match;
import lombok.Data;
import java.util.List;

@Data
public class GameDateDto {
    private String date;
    private List<GameDto> games;
}
