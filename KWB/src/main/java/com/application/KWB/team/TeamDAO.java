package com.application.KWB.team;

import java.util.List;

import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface TeamDAO {

	List<HitterDTO> findHitterListByTeam(String teamName);

	List<PitcherDTO> findPitcherListByTeam(String teamName);


}
