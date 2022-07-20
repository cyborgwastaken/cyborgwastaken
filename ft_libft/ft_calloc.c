/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_calloc.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: gcyril <marvin@42.fr>                      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2019/10/22 17:17:55 by gcyril            #+#    #+#             */
/*   Updated: 2019/10/22 17:52:36 by gcyril           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

void	*ft_calloc(size_t count, size_t size)
{
	void	*str;
	size_t	mult;

	if (count == 0 || size == 0)
	{
		count = 1;
		size = 1;
	}
	mult = count * size;
	if (!(str = malloc(mult)))
		return (NULL);
	ft_bzero(str, mult);
	return (str);
}
