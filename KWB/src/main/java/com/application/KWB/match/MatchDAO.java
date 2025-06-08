package com.application.KWB.match;

import java.util.List;

import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface MatchDAO {

	List<GameDto> getGamesByMonth(int month);

}
