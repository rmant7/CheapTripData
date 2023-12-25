package functional;

import functional.classes.*;
import maker.CSVMaker;
import maker.NewJSONMaker;
import maker.SQLMaker;
import visual.classes.LoadType;

import org.jgrapht.GraphPath;
import org.jgrapht.alg.shortestpath.DijkstraShortestPath;
import org.jgrapht.graph.DefaultEdge;
import org.jgrapht.graph.SimpleDirectedWeightedGraph;

import com.google.gson.JsonObject;

import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

public class Calculator {

	public static ArrayList<Route> calculateRoutes(ArrayList<Location> locations, ArrayList<TravelData> directRoutes,
			LoadType loadTypes, String validationFolder, String routeType, String csvFolderPath, String jsonFolderPath,
			String sqlFolderPath) {

		ArrayList<Route> routes_final = new ArrayList<>();
		int finalCount = 1;

		System.out.println("Started scanning routes");
		System.out.println("Getting locations");

		SimpleDirectedWeightedGraph<Integer, DefaultEdge> routeGraph = new SimpleDirectedWeightedGraph<>(
				DefaultEdge.class);
		for (int i = 0; i < locations.size(); i++) {
			routeGraph.addVertex(locations.get(i).getId());
		}

		for (int j = 0; j < directRoutes.size(); j++) {
			TravelData data = directRoutes.get(j);
			int Id = data.getId();
			int fromID = data.getFrom();
			int toID = data.getTo();
			float price = data.getEuro_price();
			DefaultEdge e = routeGraph.getEdge(fromID, toID);
			if (e != null) {
				System.out.println("Updating Price from: " + fromID + ", to: " + toID);
				if (routeGraph.getEdgeWeight(e) > price)
					routeGraph.setEdgeWeight(e, price);
			} else {
				if (fromID != toID) {
					System.out.println("Adding to graph from: " + fromID + ", to: " + toID);
					e = routeGraph.addEdge(fromID, toID);
					routeGraph.setEdgeWeight(e, price);
				}
			}
		}
		HashMap<Integer, Integer> counter = new HashMap<>();

		try (FileWriter csvFileWriter = new FileWriter(csvFolderPath + "/" + routeType + ".csv", true);
				FileWriter jsonFileWriter = new FileWriter(jsonFolderPath + "/" + routeType + ".json", true);
				FileWriter sqlFileWriter = new FileWriter(sqlFolderPath + "/" + routeType + ".sql", true);) {
			NewJSONMaker.folderForPartlyMaker(jsonFolderPath, routeType);
			for (Location from : locations) {
				System.out.println("Scanning from: " + from.getId());
				
				try (FileWriter jsonPartlyFileWriter = new FileWriter(
						jsonFolderPath + "/partly/" + String.valueOf(from.getId()) + ".json", true);) {
					for (Location to : locations) {
						if (to.getId() == from.getId())
							continue;
						System.out.println("--Scanning route from: " + from.getId() + " to: " + to.getId());
						GraphPath<Integer, DefaultEdge> path = DijkstraShortestPath.findPathBetween(routeGraph,
								from.getId(), to.getId());
						if (path == null)
							continue;
						List<DefaultEdge> edgeList = path.getEdgeList();
						if (edgeList == null || edgeList.size() == 0)
							continue;
						StringBuilder travelData = new StringBuilder();
						float totalPrice = 0;
						int duration = 0;
						int currentFromID = -1, currentToID = -1, bestTravelOptionID = -1;
						float minPrice = -1;
						for (int i = 0; i < edgeList.size(); i++) {
							DefaultEdge edge = edgeList.get(i);
							int edgeFrom = routeGraph.getEdgeSource(edge);
							int edgeTo = routeGraph.getEdgeTarget(edge);
							int id = 0;
							int fromID = 0;
							int toID = 0;
							float euroPrice = 10000000;
							int minutes = 0;
							for (int j = 0; j < directRoutes.size(); j++) {
								TravelData data = directRoutes.get(j);
								if (data.getFrom() == edgeFrom && data.getTo() == edgeTo) {
									if (data.getEuro_price() < euroPrice) {
										id = data.getId();
										fromID = data.getFrom();
										toID = data.getTo();
										euroPrice = data.getEuro_price();
										minutes = data.getTime_in_minutes();
									}
								}
							}
							ArrayList<DirectRoute> routes = new ArrayList<>();
							if (currentFromID == -1) {
								currentFromID = fromID;
								currentToID = toID;
								minPrice = euroPrice;
								bestTravelOptionID = id;
								totalPrice = totalPrice + minPrice;
								if (travelData.length() > 0) {
									travelData.append(",");
								}
								travelData.append(bestTravelOptionID);
								counting(counter, bestTravelOptionID);
								DirectRoute route = new DirectRoute(bestTravelOptionID, currentFromID, currentToID,
										minPrice);
								routes.add(route);
							} else if (currentFromID == fromID) {
								if (minPrice > euroPrice) {
									minPrice = euroPrice;
									bestTravelOptionID = id;
								}
								totalPrice = totalPrice + minPrice;
								if (travelData.length() > 0) {
									travelData.append(",");
								}
								travelData.append(bestTravelOptionID);
								counting(counter, bestTravelOptionID);
								DirectRoute route = new DirectRoute(bestTravelOptionID, currentFromID, currentToID,
										minPrice);
								routes.add(route);
								System.out.println("Маршрут идет по следующим direct routes " + routes);
							} else {
								currentFromID = fromID;
								currentToID = toID;
								minPrice = euroPrice;
								bestTravelOptionID = id;
								totalPrice = totalPrice + minPrice;
								if (travelData.length() > 0) {
									travelData.append(",");
								}
								travelData.append(bestTravelOptionID);
								counting(counter, bestTravelOptionID);
								DirectRoute route = new DirectRoute(bestTravelOptionID, currentFromID, currentToID,
										minPrice);
								routes.add(route);
							}
							duration = duration + minutes;
						}
						Route route1 = new Route(finalCount, from.getId(), to.getId(), totalPrice, duration,
								travelData.toString());
						finalCount++;

						//TODO encapsulate code below
						// ----------------------------------------------------------------------------
						//
						// CSV
						if (loadTypes.isCsvLoad() && !csvFolderPath.equals("")) {

							StringBuilder builder = new StringBuilder();
							builder.append("(").append(route1.getId()).append(",").append(route1.getFrom()).append(",")
									.append(route1.getEuro_price()).append(",").append(route1.getTrip_duration())
									.append(",").append(route1.getTravel_data()).append(")");
							if (from.equals(locations.get(locations.size() - 1))
									&& to.equals(locations.get(locations.size() - 2))) {
								builder.append(";");
							} else {
								builder.append(",");
							}

							csvFileWriter.write(builder.toString());
							csvFileWriter.flush();
							

						}
						// ---------------------------------------------------------------

						// Json
						if (loadTypes.isJsonLoad() && !jsonFolderPath.equals("")) {
							

							JsonObject object = new JsonObject();
							int id = route1.getFrom() * 10000 + route1.getTo();
	//						object.addProperty("id", id);
							object.addProperty("from", route1.getFrom());
							object.addProperty("to", route1.getTo());
							object.addProperty("price", (int) route1.getEuro_price());
							object.addProperty("duration", route1.getTrip_duration());
							object.addProperty("direct_routes", route1.getTravel_data());
							 JsonObject general = new JsonObject();
							 general.add(String.valueOf(id), object);

							jsonFileWriter.write(general.toString());
							jsonFileWriter.write(",");
							jsonFileWriter.flush();
							
							//Json partly
							try {

								jsonPartlyFileWriter.write(object.toString());
								jsonPartlyFileWriter.flush();

							} catch (IOException ex) {
								throw new RuntimeException(ex);
							}
						}
						// --------------------------------------------------------------------

						// SQL
						if (loadTypes.isSqlLoad() && !sqlFolderPath.equals("")) {
							if (from.equals(locations.get(0)) && to.equals(locations.get(1))) {
								String result = "DROP TABLE IF EXISTS " + routeType + ";" + "\n" + "CREATE TABLE " //TODO 
										+ routeType + "\n" + "(" + "\n"
										+ "   id                  INT                 NOT NULL," + "\n"
										+ "   `from`              INT                 NOT NULL," + "\n"
										+ "   `to`                INT                 NOT NULL," + "\n"
										+ "   euro_price          FLOAT               NOT NULL," + "\n"
										+ "   trip_duration       INT                 NOT NULL," + "\n"
										+ "   travel_data         VARCHAR(255)        NOT NULL," + "\n"
										+ "PRIMARY KEY (id)" + "\n" + ") ENGINE = InnoDB" + "\n"
										+ "DEFAULT CHARSET = utf8;" + "\n" + "LOCK TABLES " + routeType + " WRITE;"
										+ "\n"
										+ "INSERT INTO" + routeType + "(id, `from`,`to`, transportation_type, euro_price, time_in_minutes) " //TODO 
										+ "VALUES ";

								sqlFileWriter.write(result);
								sqlFileWriter.flush();

							}

							String result1 = "(" + route1.getId() + "," + route1.getFrom() + "," + route1.getTo() + ","
									+ route1.getEuro_price() + "," + route1.getTrip_duration() + ",'"
									+ route1.getTravel_data() + "')";
							if (from.equals(locations.get(locations.size() - 1))
									&& to.equals(locations.get(locations.size() - 2))) {
								result1 = result1 + ";\n";
							} else {
								result1 = result1 + ",\n";

							}

							sqlFileWriter.write(result1);
							sqlFileWriter.flush();
							
							if (from.equals(locations.get(locations.size() - 1))
									&& to.equals(locations.get(locations.size() - 2))) {
								String result2 = "UNLOCK TABLES;";
								sqlFileWriter.write(result2);
								sqlFileWriter.flush();										
							}

							
						}
						// -----------------------------------------------------------------------

						// --------------------------------------------------------------------------
						

					}
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		CSVMaker.stringMaker(routeType + ".csv created");
		NewJSONMaker.stringMaker(routeType + ".json created");
		SQLMaker.stringMaker(routeType + ".sql created");

		if (!validationFolder.equals("") && loadTypes.isValidationLoad()) {
			CSVMaker.validationToFile(Validator.validate(counter, directRoutes, routeGraph), validationFolder,
					routeType);
		}
		return routes_final;
	}

	public static ArrayList<TravelData> getFlyingData(ArrayList<TravelData> input) {
		ArrayList<TravelData> result = new ArrayList<>();
		for (int i = 0; i < input.size(); i++) {
			TravelData data = input.get(i);
			if (data.getTransportation_type() == 1) {
				result.add(data);
			}
		}
		return result;
	}

	public static ArrayList<TravelData> getFixedDataWithoutRideShare(ArrayList<TravelData> input) {
		ArrayList<TravelData> result = new ArrayList<>();
		for (int i = 0; i < input.size(); i++) {
			TravelData data = input.get(i);
			if ((data.getTransportation_type() != 1) && (data.getTransportation_type() != 8)) {
				result.add(data);
			}
		}
		return result;
	}

	public static ArrayList<TravelData> getDataWithoutRideShare(ArrayList<TravelData> input) {
		ArrayList<TravelData> result = new ArrayList<>();
		for (int i = 0; i < input.size(); i++) {
			TravelData data = input.get(i);
			if (data.getTransportation_type() != 8) {
				result.add(data);
			}
		}
		return result;
	}

	public static void counting(HashMap<Integer, Integer> counter, int travelData) {
		if (!counter.containsKey(travelData)) {
			counter.put(travelData, 1);
		} else {
			int count = counter.get(travelData);
			counter.put(travelData, count + 1);
		}
	}
}
